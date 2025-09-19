import { useState, useRef, useEffect, useCallback } from "react";

export const useCamera = () => {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [currentCamera, setCurrentCamera] = useState<'front' | 'back'>('back');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const startCamera = useCallback(async () => {
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
                console.log('Camera stream set to video element:', mediaStream);
                console.log('Video element:', videoRef.current);
            } else {
                console.log('Video ref not available yet');
            }
        } catch (err) {
            setError('Camera access denied');
            console.error('Camera error:', err);
        } finally {
            setIsLoading(false);
        }
    }, [currentCamera]); // Include currentCamera dependency

    const stopCamera = useCallback(() => {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            setStream(null);
        }
    }, [stream]);

    const switchCamera = useCallback(() => {
        stopCamera();
        setCurrentCamera(prev => prev === 'front' ? 'back' : 'front');
        // startCamera will be called automatically due to the dependency change
    }, [stopCamera]);

    const takePhoto = useCallback((): Promise<Blob | null> => {
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
    }, []);

    // Ensure video element gets the stream when it becomes available
    useEffect(() => {
        if (stream && videoRef.current) {
            videoRef.current.srcObject = stream;
            console.log('Stream assigned to video element in useEffect');
        }
    }, [stream]);

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