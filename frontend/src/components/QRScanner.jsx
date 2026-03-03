import { useEffect } from "react";
import { Html5Qrcode } from "html5-qrcode";

function QRScanner({ onScan, onError, active = true, elementId = "qr-reader" }) {
  useEffect(() => {
    if (!active) {
      return undefined;
    }

    const scanner = new Html5Qrcode(elementId, { verbose: false });
    let mounted = true;

    Html5Qrcode.getCameras()
      .then((cameras) => {
        if (!mounted) {
          return;
        }
        if (!cameras || cameras.length === 0) {
          onError?.("No camera device found.");
          return;
        }

        return scanner.start(
          cameras[0].id,
          {
            fps: 10,
            qrbox: { width: 240, height: 240 },
            aspectRatio: 1.0
          },
          (decodedText) => {
            onScan?.(decodedText);
          },
          () => {
            // Ignore decode errors while scanning frames.
          }
        );
      })
      .catch((err) => {
        onError?.(err?.message || "Unable to initialize scanner.");
      });

    return () => {
      mounted = false;
      scanner
        .stop()
        .then(() => scanner.clear())
        .catch(() => {
          scanner.clear().catch(() => {});
        });
    };
  }, [active, elementId, onError, onScan]);

  return <div id={elementId} style={{ width: "100%" }} />;
}

export default QRScanner;
