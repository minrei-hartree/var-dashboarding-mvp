"use client"

import * as React from "react"
import { Check, ChevronsUpDown } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover"
import useTraderPnlVectors from "@/hooks/useTraderPnlVectors"

const TraderSelection = () => {
  const [open, setOpen] = React.useState(false)
  const { traders, isLoadingTraders, selectedTrader, setSelectedTrader } = useTraderPnlVectors()

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-[200px] justify-between"
        >
          {selectedTrader
            ? traders?.find((trader) => trader === selectedTrader)
            : "Select Trader..."}
          <ChevronsUpDown className="opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-[200px] p-0">
        <Command>
          <CommandInput placeholder="Search Trader..." className="h-9" />
          <CommandList>
            <CommandEmpty>
              {isLoadingTraders ? "Fetching Traders..." : "No Trader Found."}
            </CommandEmpty>
            <CommandGroup>
              {traders?.map((trader) => (
                <CommandItem
                  key={trader}
                  value={trader}
                  onSelect={(currentValue) => {
                    setSelectedTrader(currentValue === selectedTrader ? "" : currentValue)
                    setOpen(false)
                  }}
                >
                  {trader}
                  <Check
                    className={cn(
                      "ml-auto",
                      selectedTrader === trader ? "opacity-100" : "opacity-0"
                    )}
                  />
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  )
}

export default TraderSelection