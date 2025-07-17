'use client';

import { useEffect, useState } from 'react';

type Document = {
  id: string;
  text: string;
  created_at: string;
  embedding: number[];
};

export default function Home() {
  const [docs, setDocs] = useState<Document[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [selectedDoc, setSelectedDoc] = useState<Document | null>(null);
  const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'MISSING_ENV';

  console.log('API_BASE =', API_BASE);

  const fetchList = async () => {
    const res = await fetch(`${API_BASE}/list`);
    const data = await res.json();
    setDocs(data);
  };

  useEffect(() => {
    fetchList();
  }, []);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    await fetch(`${API_BASE}/upload`, {
      method: 'POST',
      body: formData,
    });
    setFile(null);
    fetchList();
    setLoading(false);
  };

  const handleDelete = async (id: string) => {
    await fetch(`${API_BASE}/delete/${id}`, { method: 'DELETE' });
    fetchList();
  };

  const fetchDetail = async (id: string) => {
    const res = await fetch(`${API_BASE}/detail/${id}`);
    const data = await res.json();
    setSelectedDoc(data);
  };

  return (
    <main className="p-8 space-y-8 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold">Tải tài liệu OCR</h1>

      <div className="flex gap-2 items-center">
        <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          className="px-4 py-2 bg-black text-white rounded disabled:opacity-50"
        >
          {loading ? 'Đang tải...' : 'Tải lên'}
        </button>
      </div>

      <h2 className="text-lg font-semibold">Danh sách tài liệu</h2>
      <ul className="space-y-3">
        {docs.map((doc) => (
          <li
            key={doc.id}
            onClick={() => fetchDetail(doc.id)}
            className="cursor-pointer border p-4 rounded shadow-sm hover:bg-gray-50"
          >
            <p className="text-sm text-gray-700 mb-2">{doc.text}</p>
            <div className="text-xs text-gray-500">{doc.created_at}</div>
            <button
              onClick={e => {
                e.stopPropagation();
                handleDelete(doc.id);
              }}
              className="mt-2 text-red-600 text-sm"
            >
              Xoá
            </button>
          </li>
        ))}
      </ul>

      {selectedDoc && (
        <div className="border-t pt-4 mt-8">
          <div className="flex justify-between items-center">
            <h3 className="font-semibold text-lg">Chi tiết tài liệu</h3>
            <button onClick={() => setSelectedDoc(null)} className="text-sm text-blue-600">Đóng</button>
          </div>
          <p className="text-sm mt-2 text-gray-700 whitespace-pre-wrap">{selectedDoc.text}</p>
          <div className="text-xs text-gray-500 mt-2">ID: {selectedDoc.id}</div>
          <div className="text-xs text-gray-500">Ngày tạo: {selectedDoc.created_at}</div>
          <div className="text-xs text-gray-500 mt-1">
            Vector: {selectedDoc.embedding.slice(0, 5).map(n => n.toFixed(2)).join(', ')}...
          </div>
        </div>
      )}
    </main>
  );
}


