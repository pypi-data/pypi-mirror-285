
class saliency_generator():
    ''' Class to generate saliency maps from videos '''
    def __init__(self, model_path, model_name, model_type, device):
        ''' Initialize the class '''
        self.model_path = model_path
        self.model_name = model_name
        self.model_type = model_type
        self.device = device
        self.model = None
        self.transform = None
        self.load_model()
        self.load_transform()
        
    def load_model(self):
        ''' Load the model '''
        if self.model_type == 'torch':
            self.model = torch.load(self.model_path)
            self.model.eval()
        else:
            raise ValueError('Model type not supported')
        
    def load_transform(self):
        ''' Load the transform '''
        if self.model_type == 'torch':
            self.transform = transforms.Compose([
                transforms.Resize((224, 224)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            raise ValueError('Model type not supported')
    
    def generate_saliency(self, video_path, output_path):
        ''' Generate the saliency map '''
        cap = cv2.VideoCapture(video_path)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = self.transform(frame)
            frame = frame.unsqueeze(0)
            frame = frame.to(self.device)
            with torch.no_grad():
                saliency_map = self.model(frame)
            saliency_map = saliency_map.squeeze(0).cpu().numpy()
            saliency_map = cv2.resize(saliency_map, (224, 224))
            saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
            saliency_map = (saliency_map * 255).astype(np.uint8)
            saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
            out.write(saliency_map)
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def generate_saliency_from_images(self, image_dir, output_path):
        ''' Generate the saliency map from images '''
        image_files = os.listdir(image_dir)
        image_files.sort()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        for image_file in image_files:
            image_path = os.path.join(image_dir, image_file)
            frame = cv2.imread(image_path)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = self.transform(frame)
            frame = frame.unsqueeze(0)
            frame = frame.to(self.device)
            with torch.no_grad():
                saliency_map = self.model(frame)
            saliency_map = saliency_map.squeeze(0).cpu().numpy()
            saliency_map = cv2.resize(saliency_map, (224, 224))
            saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
            saliency_map = (saliency_map * 255).astype(np.uint8)
            saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
            out.write(saliency_map)
        out.release()
        cv2.destroyAllWindows()

    def generate_saliency_from_frames(self, frame_dir, output_path):
        ''' Generate the saliency map from frames '''
        frame_files = os.listdir(frame_dir)
        frame_files.sort()
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        for frame_file in frame_files:
            frame_path = os.path.join(frame_dir, frame_file)
            frame = cv2.imread(frame_path)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = self.transform(frame)
            frame = frame.unsqueeze(0)
            frame = frame.to(self.device)
            with torch.no_grad():
                saliency_map = self.model(frame)
            saliency_map = saliency_map.squeeze(0).cpu().numpy()
            saliency_map = cv2.resize(saliency_map, (224, 224))
            saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
            saliency_map = (saliency_map * 255).astype(np.uint8)
            saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
            out.write(saliency_map)
        out.release()
        cv2.destroyAllWindows()
    
    def generate_saliency_from_camera(self, output_path):
        ''' Generate the saliency map from camera '''
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = self.transform(frame)
            frame = frame.unsqueeze(0)
            frame = frame.to(self.device)
            with torch.no_grad():
                saliency_map = self.model(frame)
            saliency_map = saliency_map.squeeze(0).cpu().numpy()
            saliency_map = cv2.resize(saliency_map, (224, 224))
            saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
            saliency_map = (saliency_map * 255).astype(np.uint8)
            saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
            out.write(saliency_map)
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def generate_saliency_from_camera_with_face_detection(self, output_path):
        ''' Generate the saliency map from camera with face detection '''
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = Image.fromarray(face)
                face = self.transform(face)
                face = face.unsqueeze(0)
                face = face.to(self.device)
                with torch.no_grad():
                    saliency_map = self.model(face)
                saliency_map = saliency_map.squeeze(0).cpu().numpy()
                saliency_map = cv2.resize(saliency_map, (224, 224))
                saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
                saliency_map = (saliency_map * 255).astype(np.uint8)
                saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
                frame[y:y+h, x:x+w] = saliency_map
            out.write(frame)
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def generate_saliency_from_camera_with_eye_detection(self, output_path):
        ''' Generate the saliency map from camera with eye detection '''
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            eyes = eye_cascade.detectMultiScale(gray)
            for (x, y, w, h) in eyes:
                eye = frame[y:y+h, x:x+w]
                eye = cv2.cvtColor(eye, cv2.COLOR_BGR2RGB)
                eye = Image.fromarray(eye)
                eye = self.transform(eye)
                eye = eye.unsqueeze(0)
                eye = eye.to(self.device)
                with torch.no_grad():
                    saliency_map = self.model(eye)
                saliency_map = saliency_map.squeeze(0).cpu().numpy()
                saliency_map = cv2.resize(saliency_map, (224, 224))
                saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
                saliency_map = (saliency_map * 255).astype(np.uint8)
                saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
                frame[y:y+h, x:x+w] = saliency_map
            out.write(frame)
        cap.release()
        out.release()
        cv2.destroyAllWindows()

    def generate_saliency_from_camera_with_face_and_eye_detection(self, output_path):
        ''' Generate the saliency map from camera with face and eye detection '''
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (224, 224))
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                face = frame[y:y+h, x:x+w]
                face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face = Image.fromarray(face)
                face = self.transform(face)
                face = face.unsqueeze(0)
                face = face.to(self.device)
                with torch.no_grad():
                    saliency_map = self.model(face)
                saliency_map = saliency_map.squeeze(0).cpu().numpy()
                saliency_map = cv2.resize(saliency_map, (224, 224))
                saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
                saliency_map = (saliency_map * 255).astype(np.uint8)
                saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
                frame[y:y+h, x:x+w] = saliency_map
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                eyes = eye_cascade.detectMultiScale(roi_gray)
                for (ex, ey, ew, eh) in eyes:
                    eye = roi_color[ey:ey+eh, ex:ex+ew]
                    eye = cv2.cvtColor(eye, cv2.COLOR_BGR2RGB)
                    eye = Image.fromarray(eye)
                    eye = self.transform(eye)
                    eye = eye.unsqueeze(0)
                    eye = eye.to(self.device)
                    with torch.no_grad():
                        saliency_map = self.model(eye)
                    saliency_map = saliency_map.squeeze(0).cpu().numpy()
                    saliency_map = cv2.resize(saliency_map, (224, 224))
                    saliency_map = (saliency_map - np.min(saliency_map)) / (np.max(saliency_map) - np.min(saliency_map))
                    saliency_map = (saliency_map * 255).astype(np.uint8)
                    saliency_map = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
                    roi_color[ey:ey+eh, ex:ex+ew] = saliency_map
            out.write(frame)        
        cap.release()
        out.release()

