'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Generate() {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [currentCamera, setCurrentCamera] = useState<'front' | 'back'>('back')
  const [location, setLocation] = useState<{ lat: number, lng: number, address: string } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  //WebSocket
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);
  const [status, setStatus] = useState("idle");
  const [thinking, setThinking] = useState<string>(""); // live stream text
  const [error, setError] = useState<string | null>(null);
  const [done, setDone] = useState(false);
  const logEndRef = useRef<HTMLDivElement | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thinking]);

  // Get user's location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords
          try {
            // Reverse geocoding to get address
            const response = await fetch(
              `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
            )
            const data = await response.json()
            setLocation({
              lat: latitude,
              lng: longitude,
              address: `${data.city}, ${data.principalSubdivision}, ${data.countryName}`
            })
          } catch (err) {
            setLocation({
              lat: latitude,
              lng: longitude,
              address: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
            })
          }
        },
        (error) => {
          setError('Location access denied')
        }
      )
    } else {
      setError('Geolocation not supported')
    }
  }, [])

  // Start camera
  const startCamera = async () => {
    try {
      setIsLoading(true)
      const devices = await navigator.mediaDevices.enumerateDevices()
      const videoDevices = devices.filter(device => device.kind === 'videoinput')

      if (videoDevices.length === 0) {
        setError('No cameras found')
        return
      }

      const constraints = {
        video: {
          facingMode: currentCamera === 'front' ? 'user' : 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      }

      const mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
      setStream(mediaStream)

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream
      }
    } catch (err) {
      setError('Camera access denied')
    } finally {
      setIsLoading(false)
    }
  }

  // Stop camera
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }
  }

  // Switch camera
  const switchCamera = () => {
    stopCamera()
    setCurrentCamera(prev => prev === 'front' ? 'back' : 'front')
  }

  // Take photo
  const takePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')

      if (context) {
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        context.drawImage(video, 0, 0)

        // Convert to blob and handle the photo
        canvas.toBlob((blob) => {
          if (blob) {
            console.log('Photo taken:', blob)
            // Here you would send the photo to your API
          }
        }, 'image/jpeg', 0.8)
      }
    }
  }
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop())
      }
    }
  }, [stream])

  useEffect(() => {
    startCamera()
  })

  const handleGenerate = () => {
    // Close any existing socket first
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
    }
    setThinking("");
    setStatus("connecting");
    setDone(false);
    setError(null);

    const ws = new WebSocket("ws://127.0.0.1:8000/ws/generate"); // dev URL
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setStatus("connected");
      ws.send(JSON.stringify({
        type: "init",
        query: location ? location.address : "Unknown location",
        img_url: "no image provided",
      }));
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      switch (msg.type) {
        case "token":
          setThinking(prev => prev + (msg.text ?? ""));
          break;
        case "status":
          setStatus(msg.message ?? "working...");
          break;
        case "progress":
          setStatus(`${msg.step ?? "Processing"} ${msg.percent ?? 0}%`);
          break;
        case "error":
          setError(msg.message ?? "Error");
          setConnected(false);
          ws.close();
          break;
        case "done":
          setDone(true);
          setConnected(false);
          ws.close();
          break;
      }
    };

    ws.onerror = () => {
      setError("WebSocket error");
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
    };
  };

  const handleCancel = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "cancel" }));
      wsRef.current.close();
    }
  };

  useEffect(() => {
    return () => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, []);

  return (
    <div className="min-h-screen mx-4 md:mx-auto max-w-7xl">

      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 ">

        <div className="md:col-span-2 col-span-1">
          <h1 className="text-3xl text-center mb-8">Generate Ambient Music</h1>
        </div>

        <div className='col-span-1'>
          <h2 className="text-xl font-semibold mb-2">Current Context</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Location:</p>
              <p className="font-medium">
                {location ? location.address.split(',')[0] : 'Getting location...'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Time:</p>
              <p className="font-medium">
                {new Date().toLocaleString().split(',')[1]}
              </p>
            </div>
          </div>

        {/* Camera Interface */}
   
          <h2 className="text-xl font-semibold mb-4">Capture Your Environment</h2>

          <div className="space-y-4">
            {/* Video Preview */}
            {!stream ? (
              <p>No camera detected</p>
            ) : (
              <><div className="relative">
                  <video ref={videoRef} autoPlay playsInline muted className="w-full h-64 md:h-96 object-cover" />
                  <canvas
                    ref={canvasRef}
                    className="hidden" />
                </div><Button
                  onClick={takePhoto}>
                    capture
                  </Button>
                  <Button
                    onClick={switchCamera}
                    variant={'link'}>
                      switch camera
                  </Button>
                </>
            )}
          </div>
        </div>

        {/* Generate Button */}
        <div className="col-span-1">
          <h2 className="text-xl font-semibold mb-4">System Messages</h2>
          <div className="text-sm text-gray-600">Status: {status}{done ? " (done)" : ""}</div>
          {/*{error && <div className="text-red-600 text-sm">Error: {error}</div>}*/}
          <div className="bg-black text-green-200 font-mono p-3 rounded h-48 overflow-auto mb-4">
            <pre className="whitespace-pre-wrap break-words">{thinking}</pre>
            <div ref={logEndRef} />
          </div>
          <div className="flex gap-3">
            <Button
              onClick={handleGenerate}
              disabled={connected}
            >
              {connected ? "Thinking..." : "Start"}
            </Button>
            <Button onClick={handleCancel} variant={'ghost'} disabled={!connected}>Cancel</Button>
          </div>
        </div>

      </div>
    </div>
  )
}