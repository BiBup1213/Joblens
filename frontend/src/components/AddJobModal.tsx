import { FileText, Link2, ListPlus, Upload } from "lucide-react";
import { useState } from "react";
import type { FormEvent } from "react";

type AddJobModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onImportLink: (url: string) => Promise<void>;
  onImportText: (text: string) => Promise<void>;
  onImportBulk: (urls: string[]) => Promise<void>;
};

const tabs = [
  { label: "Link", icon: Link2 },
  { label: "Text", icon: FileText },
  { label: "Datei", icon: Upload },
  { label: "Mehrere Links", icon: ListPlus },
];

export function AddJobModal({
  isOpen,
  onClose,
  onImportLink,
  onImportText,
  onImportBulk,
}: AddJobModalProps) {
  const [activeTab, setActiveTab] = useState("Link");
  const [linkValue, setLinkValue] = useState("");
  const [textValue, setTextValue] = useState("");
  const [bulkValue, setBulkValue] = useState("");
  const [isImporting, setIsImporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!isOpen) {
    return null;
  }

  function resetAndClose() {
    setErrorMessage(null);
    setIsImporting(false);
    onClose();
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);

    const validationMessage = getValidationMessage();
    if (validationMessage) {
      setErrorMessage(validationMessage);
      return;
    }

    try {
      setIsImporting(true);
      if (activeTab === "Link") {
        await onImportLink(linkValue.trim());
        setLinkValue("");
      } else if (activeTab === "Text") {
        await onImportText(textValue.trim());
        setTextValue("");
      } else if (activeTab === "Mehrere Links") {
        const urls = bulkValue
          .split(/\r?\n/)
          .map((url) => url.trim())
          .filter(Boolean);
        await onImportBulk(urls);
        setBulkValue("");
      }

      if (activeTab !== "Datei") {
        resetAndClose();
      }
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Die Stelle konnte nicht importiert werden.",
      );
    } finally {
      setIsImporting(false);
    }
  }

  function getValidationMessage() {
    if (activeTab === "Link") {
      if (!linkValue.trim()) {
        return "Bitte füge einen Stellenlink ein.";
      }
      if (!looksLikeUrl(linkValue.trim())) {
        return "Bitte gib eine gültige URL ein.";
      }
    }

    if (activeTab === "Text" && !textValue.trim()) {
      return "Bitte füge den Text der Stellenanzeige ein.";
    }

    if (activeTab === "Mehrere Links") {
      const urls = bulkValue
        .split(/\r?\n/)
        .map((url) => url.trim())
        .filter(Boolean);
      if (urls.length === 0) {
        return "Bitte füge mindestens einen Link ein.";
      }
      if (!urls.some(looksLikeUrl)) {
        return "Bitte füge mindestens eine gültige URL ein.";
      }
    }

    return null;
  }

  const isImportDisabled = isImporting || activeTab === "Datei";

  return (
    <div className="modal-backdrop" role="presentation" onClick={resetAndClose}>
      <form
        className="add-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-job-title"
        onClick={(event) => event.stopPropagation()}
        onSubmit={handleSubmit}
        noValidate
      >
        <header>
          <h2 id="add-job-title">Neue Stelle hinzufügen</h2>
        </header>

        <div className="modal-tabs" role="tablist" aria-label="Importart">
          {tabs.map((tab) => {
            const Icon = tab.icon;

            return (
              <button
                className={activeTab === tab.label ? "is-active" : ""}
                key={tab.label}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.label}
                onClick={() => {
                  setActiveTab(tab.label);
                  setErrorMessage(null);
                }}
              >
                <Icon aria-hidden="true" size={17} />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="modal-body">
          {activeTab === "Link" ? (
            <>
              <input
                aria-label="Stellenlink"
                placeholder="https://www.stepstone.de/..."
                type="url"
                value={linkValue}
                onChange={(event) => setLinkValue(event.target.value)}
              />
              <p>
                JobLens erkennt die Quelle und erstellt automatisch eine
                Stellenkarte.
              </p>
            </>
          ) : activeTab === "Text" ? (
            <textarea
              aria-label="Stellentext"
              placeholder="Stellentext einfügen"
              value={textValue}
              onChange={(event) => setTextValue(event.target.value)}
            />
          ) : activeTab === "Datei" ? (
            <div className="file-drop">
              <button type="button">Datei auswählen</button>
            </div>
          ) : (
            <textarea
              aria-label="Mehrere Stellenlinks"
              placeholder="https://www.stepstone.de/..."
              value={bulkValue}
              onChange={(event) => setBulkValue(event.target.value)}
            />
          )}
          {errorMessage && (
            <p className="modal-error" role="alert">
              {errorMessage}
            </p>
          )}
        </div>

        <footer>
          <button className="modal-cancel" type="button" onClick={resetAndClose}>
            Abbrechen
          </button>
          <button
            className="modal-import"
            type="submit"
            disabled={isImportDisabled}
          >
            {isImporting ? "Importiert..." : "Importieren"}
          </button>
        </footer>
      </form>
    </div>
  );
}

function looksLikeUrl(value: string) {
  try {
    const url = new URL(value);
    return url.protocol === "http:" || url.protocol === "https:";
  } catch {
    return false;
  }
}
