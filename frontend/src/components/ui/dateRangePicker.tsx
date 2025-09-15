"use client";

import * as React from "react";
import { CalendarIcon } from "lucide-react";
import { addDays, format } from "date-fns";
import type { DateRange } from "react-day-picker";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

interface DateRangePickerProps {
  className?: string;
  date?: DateRange;
  onDateChange?: (date: DateRange | undefined) => void;
  placeholder?: string;
  side?: "left" | "right" | "top" | "bottom";
  alignContent?: "start" | "end" | "center";
  disabledFutureDays?: boolean;
}

export function DateRangePicker({
  className,
  date,
  onDateChange,
  placeholder = "Pick a date range",
  disabledFutureDays = false,
  side = "left",
  alignContent = "start",
}: DateRangePickerProps) {
  const today = new Date();
  const [selectedDate, setSelectedDate] = React.useState<DateRange | undefined>(
    date || {
      from: addDays(new Date(), -30),
      to: new Date(),
    }
  );

  React.useEffect(() => {
    if (date) {
      setSelectedDate(date);
    }
  }, [date]);

  const handleDateChange = (newDate: DateRange | undefined) => {
    setSelectedDate(newDate);
    // onDateChange?.(newDate);
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal h-9 rounded-lg bg-white",
              !selectedDate && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {selectedDate?.from ? (
              selectedDate.to ? (
                <>
                  {format(selectedDate.from, "LLL dd, y")} -{" "}
                  {format(selectedDate.to, "LLL dd, y")}
                </>
              ) : (
                format(selectedDate.from, "LLL dd, y")
              )
            ) : (
              <span>{placeholder}</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent
          className="w-auto p-0 bg-white"
          align={alignContent}
          side={side}
        >
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={selectedDate?.from}
            selected={selectedDate}
            onSelect={handleDateChange}
            numberOfMonths={2}
            disabled={(date) => date > today && disabledFutureDays}
            showOutsideDays={false}
          />
          <div className="flex justify-end">
            <Button
              className="h-8 px-4 rounded-lg m-1 text-end"
              onClick={() => onDateChange?.(selectedDate)}
            >
              Confirm
            </Button>
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
}
