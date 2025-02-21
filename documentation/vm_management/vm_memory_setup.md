To set the minimum memory for a Hyper-V virtual machine using PowerShell, follow these steps:

### **1. Ensure Dynamic Memory is Enabled**
Before setting the minimum memory, ensure that Dynamic Memory is enabled for the VM. If it's disabled, Hyper-V will not allow you to set a minimum memory value.

### **2. Use `Set-VMMemory` to Configure Minimum Memory**
The `Set-VMMemory` cmdlet allows you to adjust the memory settings of a Hyper-V virtual machine.

#### **Example Command:**
```powershell
Set-VMMemory -VMName "YourVMName" -MinimumBytes 512MB
```
Replace `"YourVMName"` with the actual name of your virtual machine, and adjust the `-MinimumBytes` value as needed.

#### **Alternative: Setting in Megabytes**
If your PowerShell session does not support size units like `MB`, specify the value in bytes:
```powershell
Set-VMMemory -VMName "YourVMName" -MinimumBytes (512 * 1MB)
```
This will set the minimum memory to **512MB**.

### **3. Verify the Configuration**
To confirm that the minimum memory has been set, run:
```powershell
Get-VMMemory -VMName "YourVMName"
```
It should display the **MinimumMemory**, **StartupMemory**, and **MaximumMemory** values.

### **4. Enable Dynamic Memory (If Needed)**
If Dynamic Memory is not enabled, use:
```powershell
Set-VMMemory -VMName "YourVMName" -DynamicMemoryEnabled $true
```
This is necessary to apply the **minimum memory setting**.
