<script lang="ts">
  type Result = { phrase: string; urls: { url: string; fetched: boolean }[] };
  type Match = { url: string; similarity: number; passages: string[] };
  type Report = {
    filename: string;
    chars: number;
    search_error: string | null;
    similarity: number;
    matches: Match[];
    results: Result[];
  };

  let file = $state<File | null>(null);
  let loading = $state(false);
  let error = $state('');
  let report = $state<Report | null>(null);

  async function downloadPdf() {
    const res = await fetch('/api/report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(report),
    });
    if (!res.ok) {
      error = 'Could not build the PDF.';
      return;
    }
    const url = URL.createObjectURL(await res.blob());
    const a = Object.assign(document.createElement('a'), { href: url, download: 'report.pdf' });
    a.click();
    URL.revokeObjectURL(url);
  }

  async function submit(e: SubmitEvent) {
    e.preventDefault();
    if (!file) return;
    loading = true;
    error = '';
    report = null;
    const body = new FormData();
    body.append('document', file);
    try {
      const res = await fetch('/api/check', { method: 'POST', body });
      const data = await res.json();
      if (res.ok) report = data;
      else error = data.error ?? `Request failed (${res.status}).`;
    } catch {
      error = 'Could not reach the server.';
    } finally {
      loading = false;
    }
  }
</script>

{#if error}<div class="alert alert-danger" role="alert">{error}</div>{/if}
{#if report}
  <div class="alert alert-success" role="status">Received {report.filename} ({report.chars} characters).</div>
{/if}

<form onsubmit={submit}>
  <div class="mb-3">
    <label for="document" class="form-label">Document (.txt, max 2 MB)</label>
    <input
      class="form-control"
      type="file"
      id="document"
      accept=".txt"
      required
      onchange={(e) => (file = e.currentTarget.files?.[0] ?? null)}
    />
  </div>
  <button class="btn btn-primary" type="submit" disabled={loading}>
    {loading ? 'Checking…' : 'Check'}
  </button>
</form>

{#if report}
  <div class="d-flex align-items-center justify-content-between mt-5">
    <h2 class="h5 mb-0">Similarity: {report.similarity}%</h2>
    <button class="btn btn-outline-secondary btn-sm" type="button" onclick={downloadPdf}>Download PDF</button>
  </div>
  {#each report.matches as m}
    <div class="card mb-3">
      <div class="card-header small">
        <a href={m.url} target="_blank" rel="noopener noreferrer">{m.url}</a>
        <span class="badge text-bg-warning">{m.similarity}%</span>
      </div>
      <ul class="list-group list-group-flush">
        {#each m.passages as p}<li class="list-group-item">“{p}”</li>{/each}
      </ul>
    </div>
  {:else}
    <p class="text-muted">No similar passages found.</p>
  {/each}
{/if}

{#if report?.results.length}
  <h2 class="h5 mt-5">Phrases and search results</h2>
  {#if report.search_error}<div class="alert alert-warning" role="alert">{report.search_error}</div>{/if}
  <ol class="list-group list-group-numbered">
    {#each report.results as r}
      <li class="list-group-item">
        “{r.phrase}”
        {#if r.urls.length}
          <ul class="small mt-1 mb-0">
            {#each r.urls as u}
              <li>
                <a href={u.url} target="_blank" rel="noopener noreferrer">{u.url}</a>
                {#if u.fetched}<span class="badge text-bg-success">fetched</span>
                {:else}<span class="badge text-bg-secondary">could not fetch</span>{/if}
              </li>
            {/each}
          </ul>
        {:else if !report.search_error}
          <div class="small text-muted">No results.</div>
        {/if}
      </li>
    {/each}
  </ol>
{/if}
