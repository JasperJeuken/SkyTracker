import { Badge } from "@/components/ui/badge";

export function AircraftDetailBadge({ icon, text }: { icon: React.ReactNode, text: string }) {
    return (
        <Badge className="mr-2" variant="secondary">
            {icon}
            <p>{text}</p>
        </Badge>
    )
}