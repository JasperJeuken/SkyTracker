import { Separator } from "./separator"

export type TooltipProps = {
    label: string,
    description?: string,
    alternatives?: string[],
};

export function ValueTooltip({label, description, alternatives}: TooltipProps) {
    return <div className="flex flex-col">
        <span className={`${description ? "text-lg" : "text-base"} font-medium`}>{label}</span>
        {description && <span className="text-base font-light">{description}</span>}
        {alternatives && alternatives.length > 0 && <Separator className="my-3" />}
        {/* {alternatives && alternatives.length > 0 && <span className="text-small font-light mb-1">Alternative units:</span>} */}
        {alternatives && alternatives.length > 0 && alternatives.map((alt) => (
            <span className="font-mono text-base">{alt}</span>
        ))}
    </div>
}