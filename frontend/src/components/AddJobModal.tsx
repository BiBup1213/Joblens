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

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setErrorMessage(null);
    setIsImporting(true);

    try {
      if (activeTab === "Link") {
        await onImportLink(linkValue.trim());
        setLinkValue("");
      } else if (activeTab === "Text") {
        await onImportText(textValue.trim());
        setTextValue("");
      } else if (activeTab === "Mehrere Links") {
        const urls = bulkValue
          .split(/\s+/)
          .map((url) => url.trim())
          .filter(Boolean);
        await onImportBulk(urls);
        setBulkValue("");
      }

      if (activeTab !== "Datei") {
        onClose();
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

  const isImportDisabled =
    isImporting ||
    (activeTab === "Link" && linkValue.trim().length === 0) ||
    (activeTab === "Text" && textValue.trim().length === 0) ||
    (activeTab === "Mehrere Links" && bulkValue.trim().length === 0) ||
    activeTab === "Datei";

  return (
    <div className="modal-backdrop" role="presentation" onClick={onClose}>
      <form
        className="add-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="add-job-title"
        onClick={(event) => event.stopPropagation()}
        onSubmit={handleSubmit}
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
          <button className="modal-cancel" type="button" onClick={onClose}>
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
