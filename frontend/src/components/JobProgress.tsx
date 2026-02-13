"use client";

import { useEffect, useState } from "react";
import { getJobStatus } from "@/lib/api";
import { Loader2, CheckCircle2, XCircle } from "lucide-react";

interface Props {
  jobId: string;
  onComplete: () => void;
}

export default function JobProgress({ jobId, onComplete }: Props) {
  const [job, setJob] = useState<any>(null);

  useEffect(() => {
    const poll = setInterval(async () => {
      try {
        const data = await getJobStatus(jobId);
        setJob(data);
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(poll);
          if (data.status === "completed") onComplete();
        }
      } catch { }
    }, 1500);
    return () => clearInterval(poll);
  }, [jobId, onComplete]);

  if (!job) return <div className="flex justify-center py-8"><Loader2 className="animate-spin w-8 h-8 text-volleyball-400" /></div>;

  const pct = job.progress || 0;

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <div className="flex items-center gap-3 mb-4">
        {job.status === "completed" ? (
          <CheckCircle2 className="w-6 h-6 text-green-400" />
        ) : job.status === "failed" ? (
          <XCircle className="w-6 h-6 text-red-400" />
        ) : (
          <Loader2 className="w-6 h-6 text-volleyball-400 animate-spin" />
        )}
        <span className="font-medium capitalize">{job.status}</span>
        <span className="text-gray-500 text-sm ml-auto">{job.message}</span>
      </div>
      <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
        <div
          className="bg-gradient-to-r from-volleyball-500 to-volleyball-400 h-full rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="text-right text-sm text-gray-500 mt-1">{pct.toFixed(1)}%</p>
    </div>
  );
}
