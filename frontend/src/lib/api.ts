import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export async function uploadVideo(file: File) {
  const form = new FormData();
  form.append("file", file);
  const { data } = await api.post("/upload", form);
  return data;
}

export async function getJobStatus(jobId: string) {
  const { data } = await api.get(`/jobs/${jobId}`);
  return data;
}

export async function getJobStats(jobId: string) {
  const { data } = await api.get(`/jobs/${jobId}/stats`);
  return data;
}

export async function listJobs() {
  const { data } = await api.get("/jobs");
  return data.jobs;
}

export function exportCSV(stats: any, filename = "volleyvision-stats.csv") {
  const rows: string[] = [];

  // Players
  rows.push("Player Stats");
  rows.push("Player ID,Frames Tracked,Distance (px),Avg Speed (px/frame)");
  for (const p of stats.players || []) {
    rows.push(`${p.player_id},${p.frames_tracked},${p.distance_covered_px},${p.avg_speed_px_per_frame}`);
  }

  rows.push("");
  rows.push("Ball Stats");
  rows.push(`Frames Tracked,${stats.ball?.total_frames_tracked}`);
  rows.push(`Avg Speed,${stats.ball?.avg_speed_px_per_frame}`);
  rows.push(`Max Speed,${stats.ball?.max_speed_px_per_frame}`);
  rows.push(`Serves,${stats.ball?.serves_detected}`);
  rows.push(`Spikes,${stats.ball?.spikes_detected}`);

  rows.push("");
  rows.push("Rallies");
  rows.push("Rally ID,Start Frame,End Frame,Duration (frames),Duration (sec)");
  for (const r of stats.rallies || []) {
    rows.push(`${r.rally_id},${r.start_frame},${r.end_frame},${r.duration_frames},${r.duration_sec}`);
  }

  const blob = new Blob([rows.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
