To ensure that **Dynamic Memory** is enabled for a Hyper-V virtual machine using PowerShell, follow these steps:

---

### **1. Check if Dynamic Memory is Enabled**
Run the following command to check the current memory settings for your VM:

```powershell
Get-VMMemory -VMName "YourVMName"
```

Look for the `DynamicMemoryEnabled` field in the output:
- If it shows **`True`**, then Dynamic Memory is already enabled.
- If it shows **`False`**, you'll need to enable it.

---

### **2. Enable Dynamic Memory (If Not Enabled)**
If Dynamic Memory is disabled, enable it with:

```powershell
Set-VMMemory -VMName "YourVMName" -DynamicMemoryEnabled $true
```

---

### **3. Confirm Dynamic Memory is Enabled**
Re-run the `Get-VMMemory` command to verify:

```powershell
Get-VMMemory -VMName "YourVMName"
```

Make sure `DynamicMemoryEnabled` now shows **`True`**.

---

### **4. Adjust Memory Settings (If Needed)**
Once Dynamic Memory is enabled, you can set:
- **Minimum Memory** (e.g., 512MB)
- **Startup Memory** (e.g., 2048MB)
- **Maximum Memory** (e.g., 8192MB)

Example:
```powershell
Set-VMMemory -VMName "YourVMName" -MinimumBytes 512MB -StartupBytes 2048MB -MaximumBytes 8192MB
```

---

### **5. Restart the VM (If Required)**
If the VM is running, changes might not take effect until it's restarted:

```powershell
Stop-VM -VMName "YourVMName" -Force
Start-VM -VMName "YourVMName"
```

---

This ensures your Hyper-V VM is using **Dynamic Memory** with the correct limits.