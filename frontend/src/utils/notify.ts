import { ElMessage } from "element-plus";

export function msgSuccess(text: string) {
  ElMessage({ message: text, type: "success", duration: 1800 });
}

export function msgError(text: string) {
  ElMessage({ message: text, type: "error", duration: 2600, showClose: true });
}

export function msgInfo(text: string) {
  ElMessage({ message: text, type: "info", duration: 1800 });
}