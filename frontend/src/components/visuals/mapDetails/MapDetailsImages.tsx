import { type AircraftPhoto, type Loadable } from "@/types/api";
import { useEffect, useState } from "react";
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel";
import { ImageOff } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { AspectRatio } from "@/components/ui/aspect-ratio";


export function MapDetailsImages({ data, className }: { data: Loadable<AircraftPhoto[]>, className?: string }) {
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
    }, [api, data]);

    return (
        <div className={`relative rounded-2xl overflow-hidden shadow-md ${className}`}>
            <Carousel setApi={setApi} opts={{ loop: true }} className="w-full max-w-lg mx-auto">
                <CarouselContent>
                    {data.status === "loading" &&
                        <CarouselItem key={0}>
                            <AspectRatio ratio={aspectRatio}>
                                <Skeleton className="h-full w-full" />
                            </AspectRatio>
                        </CarouselItem>
                    }
                    { (data.status === "error" || (data.status === "success" && data.data.length == 0)) &&
                        <CarouselItem key={0}>
                            <AspectRatio ratio={aspectRatio} className="flex items-center justify-center bg-muted">
                                <ImageOff className="h-12 w-12 text-muted-foreground" />
                            </AspectRatio>
                        </CarouselItem>
                    }
                    { data.status === "success" && data.data.length > 0 &&
                        data.data.map((photo, idx) => {
                            const domain = new URL(photo.detail_url).hostname;
                            return (
                                <CarouselItem key={idx} className="pl-0">
                                    <a href={photo.detail_url} target="_blank" rel="noopener noreferrer">
                                        <AspectRatio ratio={aspectRatio} className="relative">
                                                <img src={photo.image_url} alt={`Aircraft image ${idx + 1}`} className="h-full w-full object-cover" />
                                                <div className="absolute bottom-0 left-0 w-full bg-linear-to-t from-black/60 text-white/90 text-xs px-3 py-1">
                                                    <span className="pl-3">© {domain}</span>
                                                </div>
                                        </AspectRatio>
                                    </a>
                                </CarouselItem>
                            );
                        })
                    }
                </CarouselContent>
            </Carousel>
            <div className="absolute bottom-1 right-3 space-x-2">
                {Array.from({ length: data.status === "success" ? data.data.length : 0 }).map((_, i) => (
                    <button key={i} onClick={() => api?.scrollTo(i)} className={`w-2 h-2 rounded-full transition-colors cursor-pointer ${i == current ? "bg-white" : "bg-gray-800"}`} />
                ))}
            </div>
        </div>
    )
}