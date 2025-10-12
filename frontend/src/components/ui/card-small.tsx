import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export function SmallCard({ text, icon: Icon, tooltip, className, variant="default" }: { text: string | number, icon?: React.ElementType, tooltip?: string, className?: string, variant?: "default" | "accent" }) {
    let bgColor = "";
    let textColor = "";
    switch(variant) {
        case "default":
            bgColor = "bg-gray-50 dark:bg-gray-800";
            textColor = "text-gray-950 dark:text-gray-100";
            break;
        case "accent":
            bgColor = "bg-skytracker-light dark:bg-skytracker-dark";
            textColor = "text-skytracker-dark dark:text-skytracker-light";
            break;
    }
    return (
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className={`flex items-center gap-1 h-10 p-2 rounded-sm shadow-md ${bgColor} ${className}`}>
                        {Icon && (
                            <Icon className={`${textColor} py-0.5`} />
                        )}
                        <span className={`text-md ${textColor}`}>{text}</span>
                    </div>
                </TooltipTrigger>
                {tooltip && 
                    <TooltipContent className="max-w-xs text-sm" side="bottom">
                        {tooltip}
                    </TooltipContent>
                }
            </Tooltip>
        </TooltipProvider>
    );
}
