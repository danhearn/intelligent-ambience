import { useState, useRef, useEffect } from "react";

export const useCamera = () => {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [currentCamera, setCurrentCamera] = useState<'front' | 'back'>('back');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const startCamera = async () => {
        try {
            setIsLoading(true);
            setError(null);
            
            const devices = await navigator.mediaDevices.enumerateDevices();
            const videoDevices = devices.filter(device => device.kind === "videoinput");

            if (videoDevices.length === 0) {
                setError('No cameras found');
                return;
            }

            const constraints = {
                video: {
                    facingMode: currentCamera === 'front' ? 'user' : 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };

            const mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            setStream(mediaStream);

            if (videoRef.current) {
                videoRef.current.srcObject = mediaStream;
            }
        } catch (err) {
            setError('Camera access denied');
            console.error('Camera error:', err);
        } finally {
            setIsLoading(false);
        }
    };

    const stopCamera = () => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    };

    const switchCamera = () => {
        stopCamera();
        setCurrentCamera(prev => prev === 'front' ? 'back' : 'front');
    };

    const takePhoto = (): Promise<Blob | null> => {
        return new Promise((resolve) => {
            if (videoRef.current && canvasRef.current) {
                const canvas = canvasRef.current;
                const video = videoRef.current;
                const context = canvas.getContext('2d');

                if (context) {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    context.drawImage(video, 0, 0);

                    canvas.toBlob((blob) => {
                        resolve(blob);
                    }, 'image/jpeg', 0.8);
                } else {
                    resolve(null);
                }
            } else {
                resolve(null);
            }
        });
    };

    // Cleanup on unmount
    useEffect(() => {
        return () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        };
    }, [stream]);

    return {
        stream,
        currentCamera,
        isLoading,
        error,
        videoRef,
        canvasRef,
        startCamera,
        stopCamera,
        switchCamera,
        takePhoto
    };
};