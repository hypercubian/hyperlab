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

# Deploying Pod Network
Once your Kubernetes cluster is initialized with `kubeadm`, you need to deploy a **pod network add-on** to enable communication between pods. The most common options are **Calico**, **Flannel**, **Cilium**, and **Weave Net**. Below are the steps to deploy a pod network.

---

### **Step 1: Ensure Kubernetes Cluster is Initialized**
If you haven't already initialized your cluster, run:

```bash
sudo kubeadm init
```

After initialization, set up your kubeconfig for `kubectl`:

```bash
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

---

### **Step 2: Choose and Apply a Pod Network**
#### **Option 1: Calico (Recommended for Advanced Networking & Network Policies)**
Calico is a popular choice that supports network policies.

```bash
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml
```

---

#### **Option 2: Flannel (Lightweight & Simple)**
Flannel is a simpler overlay network.

```bash
kubectl apply -f https://github.com/flannel-io/flannel/releases/latest/download/kube-flannel.yml
```

---

#### **Option 3: Cilium (Best for eBPF & Advanced Use Cases)**
Cilium is useful for high-performance networking.

```bash
kubectl apply -f https://raw.githubusercontent.com/cilium/cilium/v1.14.2/install/kubernetes/quick-install.yaml
```

---

#### **Option 4: Weave Net (Simple & Auto-detects Network)**
Weave Net provides an alternative CNI with multicast support.

```bash
kubectl apply -f https://cloud.weave.works/k8s/net?k8s-version=$(kubectl version | base64 | tr -d '\n')
```

---

### **Step 3: Verify Pod Network Deployment**
Check if the CNI plugin pods are running:

```bash
kubectl get pods -n kube-system
```

You should see pods related to your selected network, e.g., `calico-node`, `flannel`, or `cilium`.

---

### **Step 4: Allow Scheduling on Control Plane (Optional)**
If you are running a single-node cluster, enable scheduling on the control plane:

```bash
kubectl taint nodes --all node-role.kubernetes.io/control-plane-
```

---

### **Step 5: Test Networking**
Deploy a test pod:

```bash
kubectl run nginx --image=nginx --port=80
kubectl get pods -o wide
```

If networking is working, the pod should be in a **Running** state.

---


