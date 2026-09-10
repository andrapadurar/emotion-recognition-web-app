import { useMemo, useState, useRef, useEffect, useCallback } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
  LineChart,
  Line,
  CartesianGrid,
} from "recharts";
import "./App.css";

//URL-urile endpoint-urilor expuse de backend-ul FastAPI
const IMAGE_API_URL = "http://127.0.0.1:8000/analyze-image/";
const VIDEO_API_URL = "http://127.0.0.1:8000/analyze-video/";


const LOW_CONFIDENCE_THRESHOLD = 40;

//intervalul la care sunt capturate cadrele din camera web
const WEBCAM_INTERVAL_MS = 1500;

const emotionLabels = {
  angry: "Anger",
  disgust: "Disgust",
  fear: "Fear",
  happy: "Happiness",
  sad: "Sadness",
  surprise: "Surprise",
  neutral: "Neutral",
};

const emotionColors = {
  angry: "#ff3b30",
  disgust: "#d946ef",
  fear: "#22c55e",
  happy: "#facc15",
  sad: "#3b82f6",
  surprise: "#38bdf8",
  neutral: "#9ca3af",
};

function App() {
  //stari pentru fisierele încărcate
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [fileType, setFileType] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  //stari webcam
  const [webcamActive, setWebcamActive] = useState(false);
  const [webcamError, setWebcamError] = useState("");
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);
  const streamRef = useRef(null);

  const isVideo = !webcamActive && fileType.startsWith("video");

  //chart data
  const chartData = useMemo(() => {
    const scores = isVideo
      ? result?.medie_procente_video
      : result?.detalii_procente;

    if (!scores) return [];

    return Object.entries(scores)
      .map(([name, value]) => ({
        name,
        label: emotionLabels[name] || name,
        value: Number(value.toFixed(2)),
      }))
      .sort((a, b) => b.value - a.value);
  }, [result, isVideo]);


  //datele pentru graficul temporal (video)
  const timelineData = useMemo(() => {
    if (!result?.frames) return [];

    return result.frames.map((frame) => ({
      time: frame.time_seconds,
      angry: Number(frame.detalii_procente.angry?.toFixed(2) || 0),
      disgust: Number(frame.detalii_procente.disgust?.toFixed(2) || 0),
      fear: Number(frame.detalii_procente.fear?.toFixed(2) || 0),
      happy: Number(frame.detalii_procente.happy?.toFixed(2) || 0),
      sad: Number(frame.detalii_procente.sad?.toFixed(2) || 0),
      surprise: Number(frame.detalii_procente.surprise?.toFixed(2) || 0),
      neutral: Number(frame.detalii_procente.neutral?.toFixed(2) || 0),
    }));
  }, [result]);

 
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    setFile(selectedFile);
    setResult(null);
    setError("");

    if (selectedFile) {
      setFileType(selectedFile.type);
      setPreview(URL.createObjectURL(selectedFile));
    }
  };



  const analyzeEmotion = async () => {
    if (!file) {
      setError("Please upload an image or video before starting the analysis.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    const apiUrl = file.type.startsWith("video") ? VIDEO_API_URL : IMAGE_API_URL;

    try {
      const response = await fetch(apiUrl, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "The file could not be analyzed.");
        return;
      }

      setResult(data);
    } catch (err) {
      console.error(err);
      setError("Could not connect to the backend server.");
    } finally {
      setLoading(false);
    }
  };



  const captureAndAnalyze = useCallback(async () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(async (blob) => {
      if (!blob) return;

      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      try {
        const response = await fetch(IMAGE_API_URL, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          setResult(data);
          setWebcamError("");
        }
      } catch (err) {
        console.error("Webcam analysis error:", err);
      }
    }, "image/jpeg", 0.8);
  }, []);


  
  const startWebcam = async () => {
    setWebcamError("");
    setResult(null);
    setError("");
    setFile(null);
    setPreview(null);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setWebcamActive(true);

      intervalRef.current = setInterval(captureAndAnalyze, WEBCAM_INTERVAL_MS);
    } catch (err) {
      setWebcamError("Could not access the camera. Please allow camera permissions.");
      console.error(err);
    }
  };

  const stopWebcam = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }

    setWebcamActive(false);
  };

  useEffect(() => {
  if (webcamActive && videoRef.current && streamRef.current) {
    videoRef.current.srcObject = streamRef.current;
    videoRef.current.play();
  }
}, [webcamActive]);

 
  const dominantEmotion = isVideo
    ? result?.emotie_dominanta_video
    : result?.emotie_dominanta;

  const dominantScore = chartData.length > 0 ? chartData[0].value : 0;
  const isLowConfidence = result && dominantScore < LOW_CONFIDENCE_THRESHOLD;
  const faceNotDetected = !isVideo && !webcamActive && result && result.face_detected === false;
  const webcamNoFace = webcamActive && result && result.face_detected === false;
  const noFacesInVideo = isVideo && result && result.emotie_dominanta_video === "necunoscuta";
  const isShortVideo = isVideo && result && result.durata_secunde < 1;

  return (
    <main className="page">
      <section className="hero">
        <p className="eyebrow">Facial Emotion Recognition</p>
        <h1>Human Emotion Recognition</h1>
        <p className="subtitle" style={{ textAlign: "center", maxWidth: "800px", margin: "20px auto 0 auto" }}>
          A Deep Learning application for facial emotion recognition, designed
          to analyze emotions from images and video streams through intelligent
          visual analytics.
        </p>
      </section>

      <section className="layout">
        <div className="card upload-card">

        
          {!webcamActive && (
            <>
              <div className="card-header">
                <div>
                  <h2>Upload file</h2>
                  <p>Select a facial image (JPG, JPEG, PNG) or video (MP4, AVI, MOV, MKV) for analysis.</p>
                </div>
              </div>

              <label className="upload-box">
                <input
                  type="file"
                  onChange={handleFileChange}
                />
                <span>Choose file</span>
                <small>{file ? file.name : "No file selected"}</small>
              </label>

              {preview && (
                <div className="preview">
                  {fileType.startsWith("video") ? (
                    <video src={preview} controls />
                  ) : (
                    <img src={preview} alt="Uploaded preview" />
                  )}
                </div>
              )}

              <button
                className="primary-button"
                onClick={analyzeEmotion}
                disabled={loading}
              >
                {loading ? "Analyzing..." : "Analyze emotion"}
              </button>

              {error && <p className="error">{error}</p>}

              <button
                className="secondary-button"
                onClick={startWebcam}
              >
                Live Camera
              </button>

              {webcamError && <p className="error">{webcamError}</p>}
            </>
          )}

         
          {webcamActive && (
            <>
              <div className="card-header">
                <div>
                  <h2>Live Camera</h2>
                  <p>Analyzing your facial expression in real time.</p>
                </div>
              </div>

              <div className="preview">
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  playsInline
                  style={{ width: "100%", borderRadius: "16px" }}
                />
              </div>

              
              <canvas ref={canvasRef} style={{ display: "none" }} />

              <button
                className="primary-button stop-button"
                onClick={stopWebcam}
              >
                ⏹ Stop Camera
              </button>
            </>
          )}
        </div>

        
        <div className="card result-card">
          <div className="card-header">
            <div>
              <h2>Analysis Result</h2>
              <p>
                {webcamActive
                  ? "Live emotion analysis — updated every 1.5 seconds."
                  : "The dominant emotion and confidence scores are displayed below."}
              </p>
            </div>
          </div>

          {!result && !loading && (
            <div className="empty-state">
              {webcamActive
                ? "Starting analysis..."
                : "Upload an image or video and start the analysis to view the results."}
            </div>
          )}

          {result && (
            <>
              
              {faceNotDetected && (
                <div className="warning-banner warning-no-face">
                  ⚠️ No face detected in this image.
                </div>
              )}

             
              {webcamNoFace && (
                <div className="warning-banner warning-no-face">
                  ⚠️ No face detected. Please look directly at the camera.
                </div>
              )}

             
              {noFacesInVideo && (
                <div className="warning-banner warning-no-face">
                  ⚠️ No faces were detected in any frame of this video.
                </div>
              )}

              
              {isShortVideo && !noFacesInVideo && (
                <div className="warning-banner warning-low-confidence">
                  ℹ️ Video is very short (under 1 second). Results may not be representative.
                </div>
              )}

              
              {!faceNotDetected && !webcamNoFace && !noFacesInVideo && !isShortVideo && isLowConfidence && (
                <div className="warning-banner warning-low-confidence">
                  ℹ️ Low confidence ({dominantScore}%) — the detected emotion is unclear.
                </div>
              )}

              <div className="dominant-box">
                <span>Dominant emotion</span>
                {faceNotDetected || noFacesInVideo || webcamNoFace ? (
                  <strong style={{ color: "#94a3b8", fontSize: "28px" }}>
                    N/A
                  </strong>
                ) : (
                  <strong style={{ color: emotionColors[dominantEmotion] || "#6d28d9" }}>
                    {emotionLabels[dominantEmotion] || dominantEmotion}
                  </strong>
                )}
                {!isVideo && !faceNotDetected && !webcamNoFace && result.face_confidence !== undefined && (
                  <span className="confidence-label">
                    Face confidence: {(result.face_confidence * 100).toFixed(0)}%
                  </span>
                )}
              </div>


             
              {isVideo && (
                <div className="video-stats">
                  <div>
                    <span>Duration</span>
                    <strong>{result.durata_secunde}s</strong>
                  </div>
                  <div>
                    <span>FPS</span>
                    <strong>{result.fps}</strong>
                  </div>
                  <div>
                    <span>Frames analyzed</span>
                    <strong>{result.frame_count_analyzed}</strong>
                  </div>
                </div>
              )}


              
              {!faceNotDetected && !noFacesInVideo && !webcamNoFace && (
                <>
                  <div className="chart-wrapper">
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData}>
                        <XAxis dataKey="label" tick={{ fontSize: 12 }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="value" radius={[8, 8, 0, 0]}>
                          {chartData.map((entry) => (
                            <Cell
                              key={entry.name}
                              fill={emotionColors[entry.name] || "#7c3aed"}
                              opacity={isLowConfidence ? 0.5 : 1}
                            />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="scores-grid">
                    {chartData.map((emotion) => (
                      <div className="score-item" key={emotion.name}>
                        <span>{emotion.label}</span>
                        <strong>{emotion.value}%</strong>
                      </div>
                    ))}
                  </div>
                </>
              )}


              
              {isVideo && timelineData.length > 0 && !noFacesInVideo && (
                <div className="timeline-card">
                  <h3>Temporal emotion evolution</h3>
                  <p>
                    The chart shows how confidence scores change across the
                    analyzed video frames.
                  </p>

                  <ResponsiveContainer width="100%" height={320}>
                    <LineChart data={timelineData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis
                        dataKey="time"
                        label={{
                          value: "Time (seconds)",
                          position: "insideBottom",
                          offset: -5,
                        }}
                      />
                      <YAxis />
                      <Tooltip />
                      {Object.keys(emotionLabels).map((emotion) => (
                        <Line
                          key={emotion}
                          type="monotone"
                          dataKey={emotion}
                          stroke={emotionColors[emotion]}
                          strokeWidth={2}
                          dot={false}
                        />
                      ))}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </>
          )}
        </div>
      </section>
    </main>
  );
}

export default App;
