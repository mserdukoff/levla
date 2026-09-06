export function backendUrl(): string {
  return (process.env.NLP_BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
}
