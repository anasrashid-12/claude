"use client";
import { useState } from "react";

export default function ImageUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "done" | "error">("idle");

  const handleUpload = async () => {
    if (!file) return;
    setStatus("uploading");

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://localhost:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        setStatus("done");
        setFile(null);
      } else {
        throw new Error("Upload failed");
      }
    } catch (err) {
      console.error(err);
      setStatus("error");
    }
  };

  return (
    <div className="p-4 border rounded-xl bg-white shadow max-w-md mx-auto">
      <h2 className="text-lg font-semibold mb-2">Upload Image</h2>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mb-4"
      />

      <button
        onClick={handleUpload}
        disabled={!file || status === "uploading"}
        className="px-4 py-2 bg-blue-600 text-white rounded disabled:opacity-50"
      >
        {status === "uploading" ? "Uploading..." : "Upload"}
      </button>

      {status === "done" && <p className="text-green-600 mt-2">✅ Uploaded successfully!</p>}
      {status === "error" && <p className="text-red-600 mt-2">❌ Failed to upload.</p>}
    </div>
  );
}
