"use client";

import { UploadCloud } from "lucide-react";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import toast from "react-hot-toast";
import { api } from "../../components/api";
import ScanResult from "../../components/ScanResult";

export default function DocumentsPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const onDrop = useCallback((accepted: File[]) => setFile(accepted[0]), []);
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop, accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], "text/plain": [".txt"] } });
  async function scan() {
    if (!file) return;
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await api.post("/api/scan/document", form);
      setResult(res.data);
    } catch (e: any) {
      toast.error(e.response?.data?.detail || "Document scan failed");
    }
  }
  const counts = result?.entities?.reduce((acc: any, e: any) => ({ ...acc, [e.entity_type]: (acc[e.entity_type] || 0) + 1 }), {}) || {};
  return (
    <div className="space-y-6">
      <div className="card">
        <h1 className="mb-4 text-2xl font-bold">Document Scanner</h1>
        <div {...getRootProps()} className={`rounded-lg border-2 border-dashed p-10 text-center ${isDragActive ? "border-blue-500 bg-blue-50" : "border-slate-300"}`}>
          <input {...getInputProps()} />
          <UploadCloud className="mx-auto mb-3 h-10 w-10 text-blue-600" />
          <p>{file ? file.name : "Drop PDF, DOCX, or TXT here"}</p>
        </div>
        <button className="btn mt-4" disabled={!file} onClick={scan}>Scan Document</button>
      </div>
      {result && <div className="grid gap-3 md:grid-cols-4">{Object.entries(counts).map(([k, v]: any) => <div className="card" key={k}><div className="text-2xl font-bold">{v}</div><div className="text-sm text-slate-500">{k}</div></div>)}</div>}
      <ScanResult result={result} />
    </div>
  );
}
