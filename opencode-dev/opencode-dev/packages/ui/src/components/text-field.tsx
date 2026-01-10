import { TextField as Kobalte } from "@kobalte/core/text-field"
import { createSignal, Show, splitProps } from "solid-js"
import type { ComponentProps } from "solid-js"
import { IconButton } from "./icon-button"
import { Tooltip } from "./tooltip"
import { useData } from "../context"

export interface TextFieldProps
  extends ComponentProps<typeof Kobalte.Input>,
    Partial<
      Pick<
        ComponentProps<typeof Kobalte>,
        | "name"
        | "defaultValue"
        | "value"
        | "onChange"
        | "onKeyDown"
        | "validationState"
        | "required"
        | "disabled"
        | "readOnly"
      >
    > {
  label?: string
  hideLabel?: boolean
  description?: string
  error?: string
  variant?: "normal" | "ghost"
  copyable?: boolean
  multiline?: boolean
  copiedText?: string
  copyToClipboardText?: string
  class?: string
  autofocus?: boolean
  type?: string
  placeholder?: string
}

export function TextField(props: TextFieldProps) {
  let t: (key: string) => string = (key) => key
  try {
    const data = useData()
    t = data.t
  } catch {
    // Data context not available
  }
  const [local, others] = splitProps(props, [
    "name",
    "defaultValue",
    "value",
    "onChange",
    "onKeyDown",
    "validationState",
    "required",
    "disabled",
    "readOnly",
    "class",
    "label",
    "hideLabel",
    "description",
    "error",
    "variant",
    "copyable",
    "multiline",
    "copiedText",
    "copyToClipboardText",
  ])
  const [copied, setCopied] = createSignal(false)

  async function handleCopy() {
    const value = local.value ?? local.defaultValue ?? ""
    await navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  function handleClick() {
    if (local.copyable) handleCopy()
  }

  return (
    <Kobalte
      data-component="input"
      data-variant={local.variant || "normal"}
      name={local.name}
      defaultValue={local.defaultValue}
      value={local.value}
      onChange={local.onChange}
      onKeyDown={local.onKeyDown}
      onClick={handleClick}
      required={local.required}
      disabled={local.disabled}
      readOnly={local.readOnly}
      validationState={local.validationState}
    >
      <Show when={local.label}>
        <Kobalte.Label data-slot="input-label" classList={{ "sr-only": local.hideLabel }}>
          {local.label}
        </Kobalte.Label>
      </Show>
      <div data-slot="input-wrapper">
        <Show
          when={local.multiline}
          fallback={<Kobalte.Input {...others} data-slot="input-input" class={local.class} />}
        >
          <Kobalte.TextArea {...others} autoResize data-slot="input-input" class={local.class} />
        </Show>
        <Show when={local.copyable}>
          <Tooltip value={copied() ? (local.copiedText ?? t("tooltip.copied")) : (local.copyToClipboardText ?? t("tooltip.copyToClipboard"))} placement="top" gutter={8}>
            <IconButton
              type="button"
              icon={copied() ? "check" : "copy"}
              variant="ghost"
              onClick={handleCopy}
              data-slot="input-copy-button"
            />
          </Tooltip>
        </Show>
      </div>
      <Show when={local.description}>
        <Kobalte.Description data-slot="input-description">{local.description}</Kobalte.Description>
      </Show>
      <Kobalte.ErrorMessage data-slot="input-error">{local.error}</Kobalte.ErrorMessage>
    </Kobalte>
  )
}
