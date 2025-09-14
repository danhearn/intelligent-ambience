'use client'

import { useState, useRef, useEffect } from 'react'

export default function Generate() {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [currentCamera, setCurrentCamera] = useState<'front' | 'back'>('back')
  const [location, setLocation] = useState<{lat: number, lng: number, address: string} | null>(null)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

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

  const  handleGenerate = async () => {
    const generated = await generate()
    console.log(generated)
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">Generate Ambient Music</h1>
        
        {/* Location and Time Display */}
        <div className="bg-white rounded-lg p-4 mb-6 shadow-md">
          <h2 className="text-xl font-semibold mb-2">Current Context</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Location:</p>
              <p className="font-medium">
                {location ? location.address : 'Getting location...'}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Time:</p>
              <p className="font-medium">
                {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        </div>

        {/* Camera Interface */}
        <div className="bg-white rounded-lg p-6 shadow-md">
          <h2 className="text-xl font-semibold mb-4">Capture Your Environment</h2>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          <div className="space-y-4">
            {/* Video Preview */}
            <div className="relative bg-black rounded-lg overflow-hidden">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className="w-full h-64 md:h-96 object-cover"
              />
              <canvas
                ref={canvasRef}
                className="hidden"
              />
            </div>

            {/* Camera Controls */}
            <div className="flex flex-wrap gap-4 justify-center">
              {!stream ? (
                <button
                  onClick={startCamera}
                  disabled={isLoading}
                  className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-6 py-2 rounded-lg font-medium"
                >
                  {isLoading ? 'Starting Camera...' : 'Start Camera'}
                </button>
              ) : (
                <>
                  <button
                    onClick={takePhoto}
                    className="bg-green-500 hover:bg-green-600 text-white px-6 py-2 rounded-lg font-medium"
                  >
                    Take Photo
                  </button>
                  <button
                    onClick={switchCamera}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-medium"
                  >
                    Switch Camera
                  </button>
                  <button
                    onClick={stopCamera}
                    className="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg font-medium"
                  >
                    Stop Camera
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Generate Button */}
        <div className="text-center mt-8">
          <button
            className="bg-purple-500 hover:bg-purple-600 text-white px-8 py-3 rounded-lg font-medium text-lg"
            disabled={!location}
            onClick={handleGenerate}
          >
            Generate Ambient Music
          </button>
        </div>
      </div>
    </div>
  )
}

async function generate() {
  try {
    const response = await fetch(
      "/api/generate",
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: "Generate ambient music based on my current environment and location",
          img_url: "no image provided",
          user_feedback: ""
        })
      }
    );
    if (!response.ok) {
      throw new Error("Failed to fetch data");
    }
    const result = await response.json();
    return result;
  } catch (error) {
    console.error("Error Generating:", error);
    return null;
  }
}