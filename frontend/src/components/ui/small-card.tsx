import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";

export function SmallCard({ text, description }: { text: string, description: string }) {
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className="rounded-2xl bg-white shadow-sm border border-gray-200 px-4 py-3 text-center cursor-pointer hover:shadow-md transition-shadow">
                        <span className="text-md font-medium text-gray-800">{text}</span>
                    </div>
                </TooltipTrigger>
                <TooltipContent className="max-w-xs text-sm text-gray-700" side="bottom">
                    {description}
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
