import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";


export function ValueCard({ value, label, unit="", icon: Icon, tooltip, fullWidth=false, className, variant="default" }: { value: string | number, label?: string, unit?: string, icon?: React.ElementType, tooltip?: string, fullWidth?: boolean, className?: string, variant?: "default" | "accent" }) {
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
        <TooltipProvider>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className={`px-3 py-2 pb-3 rounded-xl shadow-lg ${bgColor} ${fullWidth ? "w-full" : "w-fit"} ${className}`}>
                        {label &&(
                            <div className="mb-[0.25rem]">
                                <span className={`text-[0.75rem] font-medium ${unitColor}`}>{label}</span>
                            </div>
                        )}
                        <div className="flex items-center gap-2">
                            {Icon && (
                                <div className="flex items-center justify-center h-full">
                                    <Icon className={`w-6 h-6 ${textColor} p-0.5`} />
                                </div>
                            )}
                            <div className="flex items-center space-x-2">
                                <span className={`text-[1.1rem] font-semibold ${textColor}`}>{value}</span>
                                {unit && <span className={`text-[0.75rem] ${unitColor}`}>{unit}</span>}
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
    );
}