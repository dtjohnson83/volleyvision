"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Loader2 } from "lucide-react";
import { uploadVideo } from "@/lib/api";

export default function UploadZone({ onJobCreated }: { onJobCreated: (jobId: string) => void }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(async (files: File[]) => {
    if (!files.length) return;
    setUploading(true);
    setError(null);
    try {
      const res = await uploadVideo(files[0]);
      onJobCreated(res.job_id);
    } catch (e: any) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally {
      setUploading(false);
    }
  }, [onJobCreated]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "video/*": [".mp4", ".mov", ".avi", ".mkv"] },
    maxFiles: 1,
    disabled: uploading,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all
        ${isDragActive ? "border-volleyball-400 bg-volleyball-900/20" : "border-gray-700 hover:border-gray-500"}
        ${uploading ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center gap-4">
        {uploading ? (
          <Loader2 className="w-12 h-12 text-volleyball-400 animate-spin" />
        ) : (
          <Upload className="w-12 h-12 text-gray-500" />
        )}
        <div>
          <p className="text-lg font-medium">
            {uploading ? "Uploading..." : isDragActive ? "Drop it here!" : "Drag & drop a volleyball video"}
          </p>
          <p className="text-sm text-gray-500 mt-1">MP4, MOV, AVI, MKV supported</p>
        </div>
        {error && <p className="text-red-400 text-sm">{error}</p>}
      </div>
    </div>
  );
}
