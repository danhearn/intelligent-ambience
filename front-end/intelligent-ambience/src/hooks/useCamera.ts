import { useState, useRef, useEffect } from "react";

export const useCamera = () => {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const [currentCamera, setCurrentCamera] = useState<'front' | 'back'>('back');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<'string' | null>(null)

    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);

    const startCamera = async () => {
        try {
            setIsLoading(true)
            const devices = await navigator.mediaDevices.enumerateDevices()
            const videoDevices = devices.filter(device => device.kind === "videoinput")

            if (videoDevices.length === 0){
                setError('no camera found')
                setIsLoading(false)
                return
            }
        } catch (err) {
            setError('camera access denied')
        } 

    }

    const stopCamera = () => {

    }

    const switchCamera = () => {

    }

    const takePhoto = () => {

    }


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
    }
}