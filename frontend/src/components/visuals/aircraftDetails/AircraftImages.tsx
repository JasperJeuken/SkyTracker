import { type AircraftPhoto } from "@/types/api";
import { useEffect, useState } from "react";
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel";
import { ImageOff } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { AspectRatio } from "@/components/ui/aspect-ratio";

export function AircraftImages({ data, error, className }: { data: AircraftPhoto[] | null, error: string | null, className?: string }) {
    const [api, setApi] = useState<CarouselApi>();
    const [current, setCurrent] = useState(0);
    const aspectRatio = 16 / 9;

    // Update navigation buttons below carousel
    useEffect(() => {
        if (!api) return;
        setCurrent(api.selectedScrollSnap());
        api.on("select", () => {
            setCurrent(api.selectedScrollSnap());
        });
    }, [api, data, error]);

    return (
        <div className={`relative ${className}`}>
            <Carousel setApi={setApi} opts={{ loop: true }} className="w-full max-w-lg mx-auto shadow-lg rounded-2xl overflow-hidden">
                <CarouselContent>
                    {!data && !error &&
                        <CarouselItem key={0}>
                            <AspectRatio ratio={aspectRatio}>
                                <Skeleton className="h-full w-full" />
                            </AspectRatio>
                        </CarouselItem>
                    }
                    { !(!data && !error) && (error || !data?.length) &&
                        <CarouselItem key={0}>
                            <AspectRatio ratio={aspectRatio} className="flex items-center justify-center bg-muted">
                                <ImageOff className="h-12 w-12 text-muted-foreground" />
                            </AspectRatio>
                        </CarouselItem>
                    }
                    {data && data.length &&
                        data.map((photo, idx) => {
                            const domain = new URL(photo.detail_url).hostname;
                            return (
                                <CarouselItem key={idx}>
                                    <AspectRatio ratio={aspectRatio} className="relative">
                                        <a href={photo.detail_url} target="_blank" rel="noopener noreferrer">
                                            <img src={photo.image_url} alt={`Aircraft image ${idx + 1}`} className="h-full w-full object-cover" />
                                        </a>
                                        <div className="absolute bottom-0 left-0 w-full bg-linear-to-t from-black/60 text-white/90 text-xs px-3 py-1">
                                            © {domain}
                                        </div>
                                    </AspectRatio>
                                </CarouselItem>
                            );
                        })
                    }
                </CarouselContent>
            </Carousel>
            <div className="absolute bottom-0 right-3 space-x-2">
                {Array.from({ length: data?.length ?? 0 }).map((_, i) => (
                    <button key={i} onClick={() => api?.scrollTo(i)} className={`w-2 h-2 rounded-full transition-colors cursor-pointer ${i == current ? "bg-white" : "bg-gray-800"}`} />
                ))}
            </div>
        </div>
    )
}