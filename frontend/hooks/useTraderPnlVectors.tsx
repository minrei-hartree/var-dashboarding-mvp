import { DataRow } from "@/lib/gridDefs"
import useSWR from "swr"

const useTraderPnlVectors = () => {
  const tradersListFetcher = (url: string): Promise<string[]> =>
    fetch(url).then((res) => res.json())

  const pnlFetcher = (url: string): Promise<DataRow[]> =>
    fetch(url).then((res) => res.json())

  const { data: traders, isLoading: isLoadingTraders } = useSWR<string[]>(
    "http://localhost:8000/utils/traders",
    tradersListFetcher
  )

  const { data: selectedTrader, mutate: setSelectedTrader } = useSWR<string>(
    'selected-trader-pnl-grid',
    null,
    { fallbackData: '' }
  )

  const { data: pnlVectors, isLoading: isLoadingVectors } = useSWR<DataRow[]>(
    selectedTrader && `http://localhost:8000/var/pnl_vectors?trader=${selectedTrader}`,
    pnlFetcher
  )

  return {
    traders,
    isLoadingTraders,
    selectedTrader,
    setSelectedTrader,
    pnlVectors,
    isLoadingVectors
  }
}

export default useTraderPnlVectors