import { Dialog as Kobalte } from "@kobalte/core/dialog"
import { IconButton } from "./icon-button"
import { useData } from "../context"

export interface ImagePreviewProps {
  src: string
  alt?: string
}

export function ImagePreview(props: ImagePreviewProps) {
  let t: (key: string) => string = (key) => key
  try {
    const data = useData()
    t = data.t
  } catch {
    // Data context not available
  }
  return (
    <div data-component="image-preview">
      <div data-slot="image-preview-container">
        <Kobalte.Content data-slot="image-preview-content">
          <div data-slot="image-preview-header">
            <Kobalte.CloseButton data-slot="image-preview-close" as={IconButton} icon="close" variant="ghost" />
          </div>
          <div data-slot="image-preview-body">
            <img src={props.src} alt={props.alt ?? t("image.preview")} data-slot="image-preview-image" />
          </div>
        </Kobalte.Content>
      </div>
    </div>
  )
}
