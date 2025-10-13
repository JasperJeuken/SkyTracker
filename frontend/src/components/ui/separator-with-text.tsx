import { Separator } from "@/components/ui/separator";


export function SeparatorWithText({ text, className="", orientation="horizontal" }: { text: string, orientation?: "horizontal" | "vertical", className?: string }) {
    return orientation == "horizontal" ? (
        <div className={`relative flex items-center justify-center overflow-hidden ${className}`}>
            <Separator />
            <div className="px-2 text-center bg-card text-sm !text-gray-600 dark:!text-gray-400">{text}</div>
            <Separator />
        </div>
    ) : (
        <div className={`shrink-0 flex flex-col justify-center items-center overflow-hidden h-full gap-2 ${className}`}>
            <Separator orientation={orientation} />
            <div className="px-2 text-center bg-card text-sm !text-gray-600 dark:!text-gray-400">{text}</div>
            <Separator orientation={orientation} />
        </div>
    )
};
