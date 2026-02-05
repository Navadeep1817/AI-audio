const API_BASE =
  import.meta.env.VITE_API_BASE || "http://localhost:8000/api/v1";

/* ===================================================
   REQUEST PRESIGNED URL
   =================================================== */
export async function requestUploadUrl(fileExtension = "mp3") {
  const res = await fetch(`${API_BASE}/upload?file_extension=${fileExtension}`, {
    method: "POST",
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(`Upload init failed (${res.status}): ${body}`);
  }

  return res.json();
}

/* ===================================================
   SAFE S3 UPLOAD (NO CONTENT-TYPE LOCKING)
   =================================================== */
export async function uploadToS3(presignedUrl, file, onProgress) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.open("PUT", presignedUrl);

    // ⭐ IMPORTANT:
    // Do NOT manually set Content-Type.
    // Backend no longer signs with it.
    // Let browser handle headers automatically.

    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) {
        onProgress(Math.round((e.loaded / e.total) * 100));
      }
    };

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve();
      } else {
        console.error("S3 upload failed:", xhr.responseText);
        reject(new Error(`S3 upload failed (${xhr.status})`));
      }
    };

    xhr.onerror = () => reject(new Error("Network error"));

    xhr.send(file);
  });
}

/* ===================================================
   JOB STATUS
   =================================================== */
export async function getJobStatus(jobId) {
  const res = await fetch(`${API_BASE}/status/${jobId}`);
  if (!res.ok) throw new Error("Status fetch failed");
  return res.json();
}

/* ===================================================
   🔥 FINAL PRODUCTION UPLOAD FLOW (EXTENSION SAFE)
   =================================================== */
export async function uploadAudioFile(file, onProgress) {
  const ext = file.name.split(".").pop()?.toLowerCase() || "mp3";

  // STEP 1 — get upload url
  const { job_id, upload_url } = await requestUploadUrl(ext);

  // STEP 2 — upload to S3
  await uploadToS3(upload_url, file, onProgress);

  // STEP 3 — start pipeline AFTER upload
  await fetch(`${API_BASE}/start/${job_id}`, {
    method: "POST",
  });

  return job_id;
}
