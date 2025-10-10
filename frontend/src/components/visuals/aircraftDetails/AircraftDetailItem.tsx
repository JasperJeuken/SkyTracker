// const itemBaseClass = "aircraft-details-item bg-gray-50 backdrop-blur-md shadow-lg p-3 dark:bg-gray-800";
// const labelClass = "aircraft-details-label !text-gray-600 dark:!text-gray-400";
// const valueClass = "aircraft-details-value flex items-center gap-1";
// const unitClass = "aircraft-details-unit !text-gray-600 dark:!text-gray-400";

// export function AircraftDetailItem({ label, icon: Icon, value, unit, full = false }: { label: string, icon: React.ElementType, value: React.ReactNode, unit?: string, full?: boolean }) {
//     return (
//         <div className={`${itemBaseClass} ${full ? "aircraft-details-full" : ""}`}>
//             <span className={labelClass}>{label}</span>
//             <span className={valueClass}>
//                 <Icon className="w-4 h-4 mr-1" />
//                 {value ?? "N/A"}
//                 {unit && <span className={unitClass}>{unit ?? ""}</span>}
//             </span>
//         </div>
//     );
// }
