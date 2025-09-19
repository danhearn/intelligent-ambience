import { useState, useEffect } from 'react';

interface LocationData {
  lat: number;
  lng: number;
  address: string;
}

export const useLocation = () => {
  const [location, setLocation] = useState<LocationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
          try {
            // Reverse geocoding to get address
            const response = await fetch(
              `https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${latitude}&longitude=${longitude}&localityLanguage=en`
            );
            const data = await response.json();
            setLocation({
              lat: latitude,
              lng: longitude,
              address: `${data.city}, ${data.principalSubdivision}, ${data.countryName}`
            });
          } catch (err) {
            // Fallback to coordinates if geocoding fails
            setLocation({
              lat: latitude,
              lng: longitude,
              address: `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`
            });
          } finally {
            setIsLoading(false);
          }
        },
        (error) => {
          setError('Location access denied');
          setIsLoading(false);
        }
      );
    } else {
      setError('Geolocation not supported');
      setIsLoading(false);
    }
  }, []);

  return { location, error, isLoading };
};
