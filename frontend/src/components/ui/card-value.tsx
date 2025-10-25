import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "./skeleton";


export function ValueCard({ 
    value, 
    label, 
    unit="", 
    icon: Icon, 
    tooltip, 
    fullWidth=false, 
    className, 
    variant="default", 
    loading=false
}: {
    value: string | number, 
    label?: string, 
    unit?: string, icon?: React.ElementType, 
    tooltip?: string, 
    fullWidth?: boolean, 
    className?: string, 
    variant?: "default" | "accent", 
    loading?: boolean 
}) {
    let bgColor = "";
    let textColor = "";
    let unitColor = "";
    switch(variant) {
        case "default":
            bgColor = "bg-gray-50 dark:bg-gray-800";
            textColor = "text-gray-950 dark:text-gray-100";
            unitColor = "text-gray-500 dark:text-gray-400"
            break;
        case "accent":
            bgColor = "bg-skytracker-light dark:bg-skytracker-dark";
            textColor = "text-skytracker-dark dark:text-skytracker-light";
            unitColor = "text-skytracker-dark/80 dark:text-skytracker-light/80";
            break;
    }
    return (
        <>
            {loading ? (
                <Skeleton className={`h-18 w-25 ${className}`} />
            ): (
                <TooltipProvider>
                    <Tooltip>
                        <TooltipTrigger asChild>
                            <div className={`h-18 min-w-25 px-3 py-2 pb-3 rounded-xl ${bgColor} ${fullWidth ? "w-full" : "w-fit"} ${className}`}>
                                {label &&(
                                    <div className="mb-[0.2rem]">
                                        <span className={`text-[0.7rem] font-medium ${unitColor}`}>{label}</span>
                                    </div>
                                )}
                                <div className={`flex items-center ${label ? "" : "justify-center"}`}>
                                    {Icon && (
                                        <div className="flex items-center justify-center h-full mr-2">
                                            <Icon className={` ${textColor} p-0.5`} />
                                        </div>
                                    )}
                                    <div className="flex items-center space-x-2">
                                        <span className={`${label ? "text-[1.1rem]" : "text-[1.5rem]"} font-semibold ${textColor}`}>{value}</span>
                                        {unit && <span className={`${label ? "text-[0.8rem]" : "text-[0.9rem]"} ${unitColor}`}>{unit}</span>}
                                    </div>
                                </div>
                            </div>
                        </TooltipTrigger>
                        {tooltip && 
                            <TooltipContent className="max-w-xs text-sm" side="bottom">
                                {tooltip}
                            </TooltipContent>
                        }
                    </Tooltip>
                </TooltipProvider>
            )}
        </>
    );
}