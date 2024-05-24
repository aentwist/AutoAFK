import { useAppSelector } from "../stores";
import { selectMessageLog } from "../stores/message";

export default function Console() {
  const log = useAppSelector(selectMessageLog);

  return (
    <div>
      {log.map((line) => (
        <div key={line}>{line}</div>
      ))}
    </div>
  );
}
