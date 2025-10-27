import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Skeleton } from "./skeleton";
import { Separator } from "@/components/ui/separator";


export function ValueTooltip({ label, description, alternatives }: { label: string, description?: string, alternatives?: string[] }) {
    return <div className="flex flex-col">
        <span className={`${description ? "text-lg" : "text-base"} font-medium`}>{label}</span>
        {description && <span className="text-base font-light">{description}</span>}
        {alternatives && alternatives.length > 0 && <Separator className="my-3" />}
        {alternatives && alternatives.length > 0 && <span className="text-small font-light mb-1">Alternative units:</span>}
        {alternatives && alternatives.length > 0 && alternatives.map((alt) => (
            <span className="font-mono text-base">{alt}</span>
        ))}
    </div>
}


export function ValueCard({ 
    value, 
    label, 
    unit="", 
    icon: Icon,
    fullWidth=false, 
    className, 
    variant="default", 
    loading=false,
    tooltip=true,
    longLabel=label,
    description="",
    alternatives=[]
}: {
    value: string | number, 
    label: string, 
    unit?: string, icon?: React.ElementType,
    fullWidth?: boolean, 
    className?: string, 
    variant?: "default" | "accent", 
    loading?: boolean,
    tooltip?: boolean,
    longLabel?: string,
    description?: string,
    alternatives?: string[]
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
                <Skeleton className={`h-15 w-25 ${className}`} />
            ): (
                <TooltipProvider>
                    <Tooltip disableHoverableContent>
                        <TooltipTrigger asChild>
                            <div className={`min-w-25 px-3 py-1 pb-3 rounded-xl ${bgColor} ${fullWidth ? "w-full" : "w-fit"} ${className}`}>
                                <div className="mb-[0.1rem]">
                                    <span className={`text-[0.7rem] font-medium ${unitColor}`}>{label}</span>
                                </div>
                                <div className={`flex items-center ${label ? "" : "justify-center"}`}>
                                    {Icon && (
                                        <div className="flex items-center justify-center h-full mr-2">
                                            <Icon className={` ${textColor} p-0.5`} />
                                        </div>
                                    )}
                                    <div className="flex items-center space-x-2">
                                        <span className={`${label ? "text-[1.1rem]" : "text-[1.5rem]"} ${unit ? "font-semibold" : "font-normal"} ${textColor}`}>{value}</span>
                                        {unit && <span className={`${label ? "text-[0.8rem]" : "text-[0.9rem]"} ${unitColor}`}>{unit}</span>}
                                    </div>
                                </div>
                            </div>
                        </TooltipTrigger>
                        {tooltip && 
                            <TooltipContent className="max-w-xs text-sm p-3 pointer-events-none" side="bottom">
                                <ValueTooltip label={longLabel} description={description} alternatives={alternatives} />
                            </TooltipContent>
                        }
                    </Tooltip>
                </TooltipProvider>
            )}
        </>
    );
}