//go:build windows

package main

import (
	"syscall"
	"unsafe"
)

// showError opens a Windows message box (the exe has no console to print to).
func showError(message string) {
	title, _ := syscall.UTF16PtrFromString("Haunted House")
	text, _ := syscall.UTF16PtrFromString(message)
	box := syscall.NewLazyDLL("user32.dll").NewProc("MessageBoxW")
	const iconError = 0x10
	box.Call(0, uintptr(unsafe.Pointer(text)), uintptr(unsafe.Pointer(title)), iconError)
}
