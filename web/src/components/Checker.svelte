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

  const sorted = $derived(report ? [...report.matches].sort((a, b) => b.similarity - a.similarity) : []);

  // shortcut: fixed cut-offs picked by eye, tune them once real documents have been checked
  function level(pct: number) {
    if (pct >= 40) return { label: 'High', color: 'danger' };
    if (pct >= 15) return { label: 'Medium', color: 'warning' };
    return { label: 'Low', color: 'success' };
  }

  function domain(url: string) {
    try {
      return new URL(url).hostname.replace(/^www\./, '');
    } catch {
      return url;
    }
  }

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

<form class="card card-body mb-4" onsubmit={submit}>
  <label for="document" class="form-label fw-semibold">Document</label>
  <input
    class="form-control"
    type="file"
    id="document"
    accept=".txt"
    required
    aria-describedby="document-help"
    onchange={(e) => (file = e.currentTarget.files?.[0] ?? null)}
  />
  <div id="document-help" class="form-text">Plain text (.txt), English, up to 2 MB.</div>
  <div class="d-flex align-items-center gap-3 mt-3">
    <button class="btn btn-primary" type="submit" disabled={loading}>
      {#if loading}<span class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>Checking…{:else}Check{/if}
    </button>
    {#if loading}<span class="text-body-secondary small" role="status">Searching the web; this can take up to a minute.</span>{/if}
  </div>
</form>

{#if error}<div class="alert alert-danger" role="alert">{error}</div>{/if}

{#if report}
  {@const lv = level(report.similarity)}
  <section class="card mb-4" aria-labelledby="score-heading">
    <div class="card-body d-flex align-items-center justify-content-between gap-3 flex-wrap">
      <div>
        <h2 id="score-heading" class="h6 text-body-secondary mb-1">Similarity</h2>
        <div class="d-flex align-items-baseline gap-2">
          <span class="display-5 fw-semibold">{report.similarity}%</span>
          <span class="badge text-bg-{lv.color}">{lv.label}</span>
        </div>
        <div class="small text-body-secondary">{report.filename} · {report.chars.toLocaleString()} characters</div>
      </div>
      <button class="btn btn-outline-secondary" type="button" onclick={downloadPdf}>Download PDF</button>
    </div>
    <div class="progress rounded-0" style="height: 6px" role="progressbar" aria-label="Similarity" aria-valuenow={report.similarity} aria-valuemin="0" aria-valuemax="100">
      <div class="progress-bar bg-{lv.color}" style="width: {report.similarity}%"></div>
    </div>
  </section>

  {#if report.search_error}<div class="alert alert-warning" role="alert">{report.search_error}</div>{/if}

  <h2 class="h5 mb-3">Sources</h2>
  {#each sorted as m}
    <article class="card mb-3">
      <div class="card-header d-flex justify-content-between align-items-center gap-2">
        <a class="text-truncate" href={m.url} title={m.url} target="_blank" rel="noopener noreferrer">{domain(m.url)}</a>
        <span class="badge text-bg-{level(m.similarity).color}">{m.similarity}%</span>
      </div>
      <div class="card-body">
        {#each m.passages as p}
          <blockquote class="border-start border-3 ps-3 mb-2 text-body-secondary">{p}</blockquote>
        {/each}
      </div>
    </article>
  {:else}
    <p class="text-body-secondary">No similar passages found.</p>
  {/each}

  {#if report.results.length}
    <details class="mt-4">
      <summary class="text-body-secondary">Search details ({report.results.length} phrases)</summary>
      <ol class="list-group list-group-numbered mt-2">
        {#each report.results as r}
          <li class="list-group-item">
            “{r.phrase}”
            {#if r.urls.length}
              <ul class="small mt-1 mb-0">
                {#each r.urls as u}
                  <li>
                    <a href={u.url} title={u.url} target="_blank" rel="noopener noreferrer">{domain(u.url)}</a>
                    {#if !u.fetched}<span class="text-body-secondary">(could not fetch)</span>{/if}
                  </li>
                {/each}
              </ul>
            {:else if !report.search_error}
              <div class="small text-body-secondary">No results.</div>
            {/if}
          </li>
        {/each}
      </ol>
    </details>
  {/if}
{/if}
