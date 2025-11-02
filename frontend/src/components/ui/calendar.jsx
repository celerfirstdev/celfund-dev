import * as React from "react"
import { cn } from "@/lib/utils"

// Simplified Calendar component without react-day-picker
function Calendar({ className, ...props }) {
  return (
    <div className={cn("p-3", className)} {...props}>
      <p className="text-sm text-muted-foreground">
        Calendar component temporarily disabled for deployment
      </p>
    </div>
  );
}

Calendar.displayName = "Calendar"

export { Calendar }
