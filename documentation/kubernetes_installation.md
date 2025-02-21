# Installing Kubernetes

---
As of February 2025, the latest stable release of Kubernetes is version 1.31. To add the official Kubernetes repository to your Ubuntu server and install the necessary components, follow these steps:

1. **Install Required Dependencies**:

   Update your package list and install essential packages:

   ```bash
   sudo apt update
   sudo apt install -y apt-transport-https ca-certificates curl gnupg
   ```


2. **Add the Kubernetes Signing Key**:

   Download and add the Kubernetes GPG key:

   ```bash
   sudo mkdir -p /etc/apt/keyrings
   curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
   ```


3. **Add the Kubernetes APT Repository**:

   Add the Kubernetes repository to your APT sources list:

   ```bash
   echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
   ```


4. **Update Package List**:

   Refresh your package list to include the Kubernetes repository:

   ```bash
   sudo apt update
   ```


5. **Install Kubernetes Components**:

   Install `kubelet`, `kubeadm`, and `kubectl`:

   ```bash
   sudo apt install -y kubelet kubeadm kubectl
   ```   

   Hold the installed packages to prevent them from being automatically updated:

   ```bash
   sudo apt-mark hold kubelet kubeadm kubectl
   ```


By completing these steps, you've added the latest Kubernetes repository to your Ubuntu server and installed the necessary components. You can now proceed to initialize your Kubernetes cluster using `kubeadm`.



# Upgrading Kubernetes

---
To unhold the Kubernetes packages (`kubelet`, `kubeadm`, and `kubectl`) so that they can be updated, run the following command:

```bash
sudo apt-mark unhold kubelet kubeadm kubectl
```

After unholding, you can update and upgrade the packages as usual:

```bash
sudo apt update
sudo apt upgrade -y kubelet kubeadm kubectl
```

If you want to hold them again after upgrading, use:

```bash
sudo apt-mark hold kubelet kubeadm kubectl
```

This ensures that they don't get automatically upgraded in future system updates.

For more detailed information, refer to the official [Kubernetes installation guide for Linux](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/). 