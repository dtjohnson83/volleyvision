"use client";

import { useEffect, useState } from "react";
import { getJobStats, exportCSV } from "@/lib/api";
import CourtHeatmap from "./CourtHeatmap";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { Download, Users, CircleDot, Timer, Activity } from "lucide-react";

interface Props {
  jobId: string;
}

function StatCard({ icon: Icon, label, value, sub }: { icon: any; label: string; value: string | number; sub?: string }) {
  return (
    <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
      <div className="flex items-center gap-2 text-gray-400 text-sm mb-1">
        <Icon className="w-4 h-4" />
        {label}
      </div>
      <div className="text-2xl font-bold">{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
    </div>
  );
}

export default function Dashboard({ jobId }: Props) {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getJobStats(jobId).then(setStats).finally(() => setLoading(false));
  }, [jobId]);

  if (loading) return <div className="text-center py-12 text-gray-400">Loading analytics...</div>;
  if (!stats) return <div className="text-center py-12 text-red-400">Failed to load stats</div>;

  const playerChartData = (stats.players || []).map((p: any) => ({
    name: `P${p.player_id}`,
    distance: Math.round(p.distance_covered_px),
    speed: p.avg_speed_px_per_frame.toFixed(1),
    frames: p.frames_tracked,
  }));

  const rallyData = (stats.rallies || []).map((r: any) => ({
    name: `R${r.rally_id}`,
    duration: r.duration_sec || (r.duration_frames / (stats.fps || 30)).toFixed(1),
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Match Analytics</h2>
        <button
          onClick={() => exportCSV(stats)}
          className="flex items-center gap-2 bg-volleyball-600 hover:bg-volleyball-700 text-white px-4 py-2 rounded-lg transition text-sm"
        >
          <Download className="w-4 h-4" /> Export CSV
        </button>
      </div>

      {/* Video player */}
      <div className="bg-gray-900 rounded-xl p-4 border border-gray-800">
        <h3 className="text-lg font-semibold mb-3">Annotated Video</h3>
        <video
          controls
          className="w-full rounded-lg max-h-[500px]"
          src={`/output/${jobId}_annotated.mp4`}
        />
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Players Tracked" value={stats.players?.length || 0} />
        <StatCard icon={CircleDot} label="Ball Frames" value={stats.ball?.total_frames_tracked || 0} />
        <StatCard icon={Timer} label="Rallies" value={stats.rallies?.length || 0} />
        <StatCard icon={Activity} label="Duration" value={`${stats.video_duration_sec?.toFixed(1)}s`} sub={`${stats.total_frames} frames @ ${stats.fps?.toFixed(1)} fps`} />
      </div>

      {/* Ball stats */}
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <h3 className="text-lg font-semibold mb-3">Ball Stats</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div><div className="text-2xl font-bold text-volleyball-400">{stats.ball?.serves_detected || 0}</div><div className="text-xs text-gray-500">Serves</div></div>
          <div><div className="text-2xl font-bold text-volleyball-400">{stats.ball?.spikes_detected || 0}</div><div className="text-xs text-gray-500">Spikes</div></div>
          <div><div className="text-2xl font-bold text-volleyball-400">{stats.ball?.blocks_detected || 0}</div><div className="text-xs text-gray-500">Blocks</div></div>
          <div><div className="text-2xl font-bold text-volleyball-400">{stats.ball?.digs_detected || 0}</div><div className="text-xs text-gray-500">Digs</div></div>
        </div>
      </div>

      {/* Player distance chart */}
      {playerChartData.length > 0 && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold mb-3">Player Distance Covered (px)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={playerChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #333" }} />
              <Bar dataKey="distance" fill="#f97316" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Rally timeline */}
      {rallyData.length > 0 && (
        <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
          <h3 className="text-lg font-semibold mb-3">Rally Duration (sec)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={rallyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" />
              <YAxis stroke="#888" />
              <Tooltip contentStyle={{ background: "#1a1a2e", border: "1px solid #333" }} />
              <Bar dataKey="duration" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Court heatmap */}
      <CourtHeatmap zoneData={stats.zone_heatmap || {}} />
    </div>
  );
}
