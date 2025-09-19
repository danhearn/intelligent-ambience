'use client'

import { useRef, useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { useCamera } from '@/hooks/useCamera'
import { useWebSocket } from '@/hooks/useWebSocket'
import { useLocation } from '@/hooks/useLocation'

export default function Generate() {
  // Camera hook
  const {
    stream,
    isLoading: cameraLoading,
    error: cameraError,
    videoRef,
    canvasRef,
    startCamera,
    switchCamera,
    takePhoto
  } = useCamera()

  // Location hook
  const { location, error: locationError, isLoading: locationLoading } = useLocation()
  
  // WebSocket hook
  const {
    connected,
    status,
    thinking,
    error: wsError,
    done,
    connect,
    disconnect
  } = useWebSocket("ws://127.0.0.1:8000/ws/generate")
  
  // Time state for live updates
  const [currentTime, setCurrentTime] = useState(new Date())
  
  const logEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thinking]);

  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  // Start camera on mount
  useEffect(() => {
    startCamera()
  }, [startCamera])

  const handleGenerate = () => {
    connect({
      query: location ? location.address : "Unknown location",
      img_url: "no image provided",
    });
  };

  const handleCancel = () => {
    disconnect();
  };

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
                {locationLoading ? 'Getting location...' : 
                 locationError ? 'Location unavailable' :
                 location ? location.address.split(',')[0] : 'Unknown'}
              </p>
              {locationError && (
                <p className="text-xs text-red-500">{locationError}</p>
              )}
            </div>
            <div>
              <p className="text-sm text-gray-600">Time:</p>
              <p className="font-medium">
                {currentTime.toLocaleString().split(',')[1]}
              </p>
            </div>
          </div>

        {/* Camera Interface */}
          <h2 className="text-xl font-semibold mb-4">Capture Your Environment</h2>

          <div className="space-y-4">
            {/* Error Display */}
            {cameraError && (
              <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
                {cameraError}
              </div>
            )}

            {/* Loading State */}
            {cameraLoading && (
              <div className="text-gray-600 text-sm">
                Starting camera...
              </div>
            )}

            {/* Video Preview */}
            {!stream && !cameraLoading ? (
              <p className="text-gray-600">No camera detected</p>
            ) : stream ? (
              <>
                <div className="relative">
                  <video ref={videoRef} autoPlay playsInline muted className="w-full h-64 md:h-96 object-cover rounded" />
                  <canvas ref={canvasRef} className="hidden" />
                </div>
                <div className="flex gap-2">
                  <Button onClick={async () => {
                    const photo = await takePhoto()
                    if (photo) {
                      console.log('Photo taken:', photo)
                      // Here you would send the photo to your API
                    }
                  }}>
                    Capture
                  </Button>
                  <Button onClick={switchCamera} variant="outline">
                    Switch Camera
                  </Button>
                </div>
              </>
            ) : null}
          </div>
        </div>

        {/* Generate Button */}
        <div className="col-span-1">
          <h2 className="text-xl font-semibold mb-4">System Messages</h2>
          <div className="text-sm text-gray-600">Status: {status}{done ? " (done)" : ""}</div>
          {wsError && <div className="text-red-600 text-sm bg-red-50 p-2 rounded mt-2">Error: {wsError}</div>}
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