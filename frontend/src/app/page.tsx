"use client";

import { useState } from "react";
import UploadZone from "@/components/UploadZone";
import JobProgress from "@/components/JobProgress";
import Dashboard from "@/components/Dashboard";

type Stage = "upload" | "processing" | "results";

export default function Home() {
  const [stage, setStage] = useState<Stage>("upload");
  const [jobId, setJobId] = useState<string | null>(null);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2">
        <h1 className="text-4xl md:text-5xl font-bold">
          <span className="bg-gradient-to-r from-volleyball-300 to-volleyball-500 bg-clip-text text-transparent">
            VolleyVision
          </span>
        </h1>
        <p className="text-gray-400 text-lg">AI-powered volleyball video analytics</p>
      </div>

      {/* Sport selector (extensible) */}
      <div className="flex justify-center">
        <div className="inline-flex bg-gray-900 rounded-lg p-1 border border-gray-800">
          <button className="px-4 py-2 rounded-md bg-volleyball-600 text-white text-sm font-medium">
            🏐 Volleyball
          </button>
          <button className="px-4 py-2 rounded-md text-gray-500 text-sm cursor-not-allowed" disabled>
            ⚽ Soccer (coming soon)
          </button>
          <button className="px-4 py-2 rounded-md text-gray-500 text-sm cursor-not-allowed" disabled>
            🏀 Basketball (coming soon)
          </button>
        </div>
      </div>

      {stage === "upload" && (
        <UploadZone
          onJobCreated={(id) => {
            setJobId(id);
            setStage("processing");
          }}
        />
      )}

      {stage === "processing" && jobId && (
        <JobProgress jobId={jobId} onComplete={() => setStage("results")} />
      )}

      {stage === "results" && jobId && <Dashboard jobId={jobId} />}

      {stage !== "upload" && (
        <div className="text-center">
          <button
            onClick={() => { setStage("upload"); setJobId(null); }}
            className="text-sm text-gray-500 hover:text-white transition"
          >
            ← Upload another video
          </button>
        </div>
      )}
    </div>
  );
}
