/**
 * useApi — Composable for LitPilot backend API calls.
 */

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:7777'

/**
 * Infer intent from a user's research session description and optional images.
 * Uses AgentOS /agents/{id}/runs endpoints for the 2-stage pipeline.
 *
 * @param {string} description
 * @param {Array<{url: string}>} [images] - array of base64 image objects
 * @returns {Promise<{summaries: string, intent: object}>}
 */
export async function inferIntent(description, images = []) {
    const isImage = images && images.length > 0;
    const agentId = isImage ? 'vision-summarizer' : 'text-summarizer';

    // -----------------------------------------------------
    // Stage 1: Summarizer
    // -----------------------------------------------------
    let promptText = `Here is the user's description of their research session:\n\n${description}\n\nProduce the structured JSON summaries for each step.`;

    const stage1Form = new FormData();
    stage1Form.append('message', promptText);
    stage1Form.append('stream', 'false');

    // Convert base64 Data URLs back to Blobs for AgentOS file upload
    if (isImage) {
        for (let i = 0; i < images.length; i++) {
            const res = await fetch(images[i].url);
            const blob = await res.blob();
            stage1Form.append('files', blob, `screenshot_${i}.jpg`);
        }
    }

    let res = await fetch(`${API_BASE}/agents/${agentId}/runs`, {
        method: 'POST',
        body: stage1Form,
    });

    if (!res.ok) {
        throw new Error(`Summarizer agent failed: ${res.statusText}`);
    }

    let data = await res.json();
    const summariesText = data.content;

    // -----------------------------------------------------
    // Stage 2: Aggregator
    // -----------------------------------------------------
    const aggPrompt = `Here are the structured step summaries from a user's research session:\n\n${summariesText}\n\nInfer the user's precise high-level research goal.`;
    const stage2Form = new FormData();
    stage2Form.append('message', aggPrompt);
    stage2Form.append('stream', 'false');

    res = await fetch(`${API_BASE}/agents/intent-aggregator/runs`, {
        method: 'POST',
        body: stage2Form,
    });

    if (!res.ok) {
        throw new Error(`Aggregator agent failed: ${res.statusText}`);
    }

    data = await res.json();
    const intentText = data.content;

    let intentData;
    try {
        if (intentText.includes("```json")) {
            const cleaned = intentText.split("```json")[1].split("```")[0].trim();
            intentData = JSON.parse(cleaned);
        } else {
            intentData = JSON.parse(intentText);
        }
    } catch {
        intentData = { inferred_intent: intentText, confidence: 0.5 };
    }

    return {
        summaries: summariesText,
        intent: intentData
    };
}

/**
 * Execute research intent via SSE stream directly targeting AgentOS executor agent.
 * @param {string} intent
 * @param {function} onEvent  - callback(eventData) for each SSE event
 * @param {function} onDone   - callback(reportContent) when complete
 * @param {function} onError  - callback(errorMessage) on failure
 * @returns {{ close: function }}  - call close() to abort
 */
export function executeResearch(intent, { onEvent, onDone, onError }) {
    const controller = new AbortController();

    (async () => {
        try {
            const formData = new FormData();
            formData.append('message', `Execute the following research intent and produce a complete literature review report:\n\n${intent}`);
            formData.append('stream', 'true');

            // Send initial manual status
            onEvent?.({ type: 'status', message: 'Delegating task to LitPilot Executor (AgentOS)...' });

            const res = await fetch(`${API_BASE}/agents/litpilot-executor/runs`, {
                method: 'POST',
                body: formData,
                signal: controller.signal,
            });

            if (!res.ok) {
                const errText = await res.text();
                onError?.(`Execution request failed: ${res.status} ${errText}`);
                return;
            }

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let finalReport = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // keep incomplete line in buffer

                for (const line of lines) {
                    if (!line.startsWith('data:')) continue;
                    const raw = line.slice(5).trim();
                    if (!raw || raw === '[DONE]') continue;

                    try {
                        const event = JSON.parse(raw);

                        // AgentOS streams incremental content chunks under `content`
                        if (event.content && typeof event.content === 'string') {
                            finalReport += event.content;
                        }

                        // We also get metrics, tool calls, and status updates we could parse
                        if (event.event === 'RunStarted') {
                            onEvent?.({ type: 'status', message: 'Agent started processing request.' });
                        }
                    } catch {
                        // skip non-JSON
                    }
                }
            }

            onEvent?.({ type: 'status', message: 'Agent completed execution.' });
            onDone?.(finalReport);

        } catch (err) {
            if (err.name !== 'AbortError') {
                onError?.(err.message);
            }
        }
    })();

    return { close: () => controller.abort() };
}
