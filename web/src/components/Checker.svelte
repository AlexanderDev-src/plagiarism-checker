<script lang="ts">
  type Result = { phrase: string; urls: { url: string; fetched: boolean }[] };
  type Report = { filename: string; chars: number; search_error: string | null; results: Result[] };

  let file = $state<File | null>(null);
  let loading = $state(false);
  let error = $state('');
  let report = $state<Report | null>(null);

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
