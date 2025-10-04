import { useEffect, useState } from "react";
import { ImageOff } from "lucide-react";
import { Carousel, CarouselContent, CarouselItem, type CarouselApi } from "@/components/ui/carousel";
import { type AircraftPhoto } from "@/types/api";

export function AircraftDetailImages({ images }: { images: AircraftPhoto[] }) {
    const has_images = images && images.length > 0
    const [api, setApi] = useState<CarouselApi>();
    const [current, setCurrent] = useState(0);
    const [count, setCount] = useState(0);

    useEffect(() => {
        if (!api) return;

        setCount(api.scrollSnapList().length);
        setCurrent(api.selectedScrollSnap());

        api.on("select", () => {
            setCurrent(api.selectedScrollSnap());
        });
    }, [api])

    return (
        <div>
            <Carousel setApi={setApi} opts={{ loop: true }} className="w-full max-w-lg mx-auto mt-4 shadow-lg rounded-2xl">
                <CarouselContent>
                    { !has_images ? 
                        <CarouselItem key={0}>
                            <div className="aspect-[16-9] w-full overflow-hidden rounded-2xl flex flex-col">
                                <div className="aspect-[16/9] w-full overflow-hidden rounded-t-2xl flex items-center justify-center bg-muted">
                                    <ImageOff className="h-12 w-12 text-muted-foreground" />
                                </div>
                                <div className="bg-white/70 dark:bg-gray-800/80 text-xs text-center py-1 rounded-b-2xl">
                                    No images found...
                                </div>
                            </div>
                        </CarouselItem>
                        : 
                        images.map((img, idx) => {
                            const domain = new URL(img.detail_url).hostname;
                            return (
                                <CarouselItem key={idx}>
                                    <a href={img.detail_url} target="_blank" rel="noopener noreferrer">
                                        <div className="aspect-[16-9] w-full overflow-hidden rounded-2xl flex flex-col">
                                                    <div className="aspect-[16/9] w-full overflow-hidden rounded-t-2xl">
                                                        <img src={img.image_url} alt={`Aircraft ${idx + 1}`} className="h-full w-full object-cover" />
                                                    </div>
                                            <div className="bg-white/70 dark:bg-gray-800/80 text-xs text-center py-1 rounded-b-2xl">
                                                © {domain}
                                            </div>
                                        </div>
                                    </a>
                                </CarouselItem>
                            )
                        })
                    }
                </CarouselContent>
            </Carousel>
            {has_images && (
                <div className="flex justify-center mt-3 space-x-2">
                        {Array.from({ length: count}).map((_, i) => (
                            <button key={i} onClick={() => api?.scrollTo(i)} 
                                className={`w-2.5 h-2.5 rounded-full transition-colors ${i == current ? "bg-black dark:bg-white" : "bg-gray-400 dark:bg-gray-600"}`} />
                        ))}
                </div>
            )}
        </div>
    );
}
