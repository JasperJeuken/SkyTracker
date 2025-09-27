import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from "@/components/ui/carousel";
import { type AircraftImage } from "./AircraftDetails";

export function AircraftDetailImages({ images }: { images: AircraftImage[] }) {
    if (!images || images.length == 0) return null;

    return (
        <Carousel className="w-full max-w-lg mx-auto mt-4">
            <CarouselContent>
                {images.map((img, idx) => (
                    <CarouselItem key={idx}>
                        <a href={img.detail_url} target="_blank" rel="noopener noreferrer">
                            <div className="aspect-[16/9] w-full overflow-hidden rounded-2xl">
                                <img src={img.image_url} alt={`Aircraft ${idx + 1}`} className="h-full w-full object-cover" />
                            </div>
                        </a>
                    </CarouselItem>
                ))}
            </CarouselContent>
            <CarouselPrevious className="absolute left-2 top-1/2 -translate-y-1/2 big-white/70 dark:bg-gray-800/70 rounded-full shadow-md" />
            <CarouselNext className="absolute right-2 top-1/2 -translate-y-1/2 big-white/70 dark:bg-gray-800/70 rounded-full shadow-md" />
        </Carousel>
    );
}
