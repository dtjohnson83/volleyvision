"use client";

import { useEffect, useState } from "react";
import { listJobs } from "@/lib/api";
import Dashboard from "@/components/Dashboard";
import { Clock, CheckCircle2, XCircle, Loader2 } from "lucide-react";

const statusIcon: Record<string, any> = {
  completed: <CheckCircle2 className="w-4 h-4 text-green-400" />,
  failed: <XCircle className="w-4 h-4 text-red-400" />,
  processing: <Loader2 className="w-4 h-4 text-volleyball-400 animate-spin" />,
  pending: <Clock className="w-4 h-4 text-gray-400" />,
};

export default function ResultsPage() {
  const [jobs, setJobs] = useState<any[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    listJobs().then(setJobs);
  }, []);

  if (selected) {
    return (
      <div>
        <button onClick={() => setSelected(null)} className="text-sm text-gray-500 hover:text-white mb-4">← Back to jobs</button>
        <Dashboard jobId={selected} />
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Past Analyses</h1>
      {jobs.length === 0 && <p className="text-gray-500">No jobs yet. Upload a video to get started.</p>}
      {jobs.map((job) => (
        <div
          key={job.id}
          onClick={() => job.status === "completed" && setSelected(job.id)}
          className={`bg-gray-900 rounded-xl p-4 border border-gray-800 flex items-center justify-between
            ${job.status === "completed" ? "cursor-pointer hover:border-volleyball-600" : "opacity-60"}`}
        >
          <div className="flex items-center gap-3">
            {statusIcon[job.status] || statusIcon.pending}
            <div>
              <div className="font-medium">{job.original_filename || job.id}</div>
              <div className="text-xs text-gray-500">{job.created_at}</div>
            </div>
          </div>
          <span className="text-sm capitalize text-gray-400">{job.status}</span>
        </div>
      ))}
    </div>
  );
}
