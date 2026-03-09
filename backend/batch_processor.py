import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import uuid
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class BatchStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class BatchJob:
    id: str
    files: List[Dict[str, Any]]  # List of file info
    status: BatchStatus
    created_at: float
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    results: List[Dict[str, Any]] = None
    error: Optional[str] = None
    progress: int = 0
    total_files: int = 0

class BatchProcessor:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, BatchJob] = {}
        self.is_processing = False
        self.processing_queue = asyncio.Queue()
        self.face_recognition_service = None
    
    def set_face_recognition_service(self, service):
        """Set the face recognition service for processing"""
        self.face_recognition_service = service
        logger.info("Face recognition service set for batch processing")
        
    def create_batch_job(self, files: List[Dict[str, Any]]) -> str:
        """Create a new batch processing job"""
        job_id = str(uuid.uuid4())
        
        job = BatchJob(
            id=job_id,
            files=files,
            status=BatchStatus.PENDING,
            created_at=time.time(),
            total_files=len(files),
            results=[]
        )
        
        self.jobs[job_id] = job
        logger.info(f"Created batch job {job_id} with {len(files)} files")
        
        # Add to processing queue
        asyncio.create_task(self._add_to_queue(job_id))
        
        return job_id
    
    async def _add_to_queue(self, job_id: str):
        """Add job to processing queue"""
        await self.processing_queue.put(job_id)
    
    async def start_processing(self):
        """Start the batch processing loop"""
        if self.is_processing:
            return
        
        self.is_processing = True
        logger.info("Starting batch processing loop")
        
        while self.is_processing:
            try:
                # Get next job from queue
                job_id = await asyncio.wait_for(self.processing_queue.get(), timeout=1.0)
                
                # Process the job
                await self._process_job(job_id)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error in batch processing loop: {e}")
                await asyncio.sleep(1)
    
    async def stop_processing(self):
        """Stop the batch processing loop"""
        self.is_processing = False
        logger.info("Stopping batch processing loop")
    
    async def _process_job(self, job_id: str):
        """Process a single batch job"""
        if job_id not in self.jobs:
            logger.error(f"Job {job_id} not found")
            return
        
        job = self.jobs[job_id]
        
        try:
            # Update job status
            job.status = BatchStatus.PROCESSING
            job.started_at = time.time()
            
            logger.info(f"Processing batch job {job_id} with {job.total_files} files")
            
            # Process files in parallel
            tasks = []
            for i, file_info in enumerate(job.files):
                task = asyncio.create_task(
                    self._process_single_file(file_info, job_id, i)
                )
                tasks.append(task)
            
            # Wait for all files to be processed
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            job.results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    job.results.append({
                        "file_index": i,
                        "file_name": job.files[i].get("filename", f"file_{i}"),
                        "error": str(result),
                        "success": False
                    })
                else:
                    job.results.append({
                        "file_index": i,
                        "file_name": job.files[i].get("filename", f"file_{i}"),
                        "result": result,
                        "success": True
                    })
            
            # Update job status
            job.status = BatchStatus.COMPLETED
            job.completed_at = time.time()
            job.progress = 100
            
            logger.info(f"Completed batch job {job_id} in {job.completed_at - job.started_at:.2f}s")
            
        except Exception as e:
            logger.error(f"Error processing batch job {job_id}: {e}")
            job.status = BatchStatus.FAILED
            job.error = str(e)
            job.completed_at = time.time()
    
    async def _process_single_file(self, file_info: Dict[str, Any], job_id: str, file_index: int) -> Dict[str, Any]:
        """Process a single file in the batch"""
        try:
            # This is a placeholder for actual file processing
            # In a real implementation, you'd call your face recognition service here
            
            # Simulate processing time
            await asyncio.sleep(0.5)
            
            # Update progress
            if job_id in self.jobs:
                self.jobs[job_id].progress = int(((file_index + 1) / self.jobs[job_id].total_files) * 100)
            
            # Return mock result
            return {
                "file_name": file_info.get("filename", f"file_{file_index}"),
                "matches_found": 3,
                "processing_time": 0.5,
                "similarity_scores": [0.85, 0.78, 0.72],
                "detected_attributes": {
                    "gender": "Female",
                    "age": 28
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing file {file_index} in job {job_id}: {e}")
            raise e
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a batch job"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        
        return {
            "id": job.id,
            "status": job.status.value,
            "progress": job.progress,
            "total_files": job.total_files,
            "processed_files": len(job.results) if job.results else 0,
            "created_at": job.created_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "processing_time": (job.completed_at - job.started_at) if job.started_at and job.completed_at else None,
            "error": job.error
        }
    
    def get_job_results(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get the results of a completed batch job"""
        if job_id not in self.jobs:
            return None
        
        job = self.jobs[job_id]
        
        if job.status != BatchStatus.COMPLETED:
            return {
                "error": f"Job not completed. Status: {job.status.value}",
                "status": job.status.value
            }
        
        return {
            "id": job.id,
            "status": job.status.value,
            "total_files": job.total_files,
            "results": job.results,
            "summary": self._generate_job_summary(job)
        }
    
    def _generate_job_summary(self, job: BatchJob) -> Dict[str, Any]:
        """Generate a summary of the batch job results"""
        if not job.results:
            return {}
        
        successful_results = [r for r in job.results if r.get("success", False)]
        failed_results = [r for r in job.results if not r.get("success", False)]
        
        # Calculate statistics
        total_matches = sum(
            r.get("result", {}).get("matches_found", 0) 
            for r in successful_results
        )
        
        avg_processing_time = sum(
            r.get("result", {}).get("processing_time", 0) 
            for r in successful_results
        ) / len(successful_results) if successful_results else 0
        
        # Gender distribution
        gender_dist = {}
        for r in successful_results:
            gender = r.get("result", {}).get("detected_attributes", {}).get("gender", "Unknown")
            gender_dist[gender] = gender_dist.get(gender, 0) + 1
        
        return {
            "total_files": job.total_files,
            "successful_files": len(successful_results),
            "failed_files": len(failed_results),
            "success_rate": (len(successful_results) / job.total_files) * 100,
            "total_matches_found": total_matches,
            "average_processing_time": avg_processing_time,
            "gender_distribution": gender_dist,
            "processing_duration": (job.completed_at - job.started_at) if job.started_at and job.completed_at else None
        }
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a batch job"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        if job.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED]:
            return False
        
        job.status = BatchStatus.CANCELLED
        job.completed_at = time.time()
        
        logger.info(f"Cancelled batch job {job_id}")
        return True
    
    def list_jobs(self, status_filter: Optional[BatchStatus] = None) -> List[Dict[str, Any]]:
        """List all batch jobs, optionally filtered by status"""
        jobs = []
        
        for job in self.jobs.values():
            if status_filter is None or job.status == status_filter:
                jobs.append(self.get_job_status(job.id))
        
        # Sort by creation time (newest first)
        jobs.sort(key=lambda x: x["created_at"], reverse=True)
        
        return jobs
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        jobs_to_remove = []
        
        for job_id, job in self.jobs.items():
            if (job.status in [BatchStatus.COMPLETED, BatchStatus.FAILED, BatchStatus.CANCELLED] and
                current_time - job.created_at > max_age_seconds):
                jobs_to_remove.append(job_id)
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]
            logger.info(f"Cleaned up old job {job_id}")
        
        return len(jobs_to_remove)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get overall processing statistics"""
        total_jobs = len(self.jobs)
        
        if total_jobs == 0:
            return {
                "total_jobs": 0,
                "status_distribution": {},
                "average_processing_time": 0,
                "total_files_processed": 0
            }
        
        status_counts = {}
        processing_times = []
        total_files = 0
        
        for job in self.jobs.values():
            status = job.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
            
            if job.started_at and job.completed_at:
                processing_times.append(job.completed_at - job.started_at)
            
            total_files += job.total_files
        
        return {
            "total_jobs": total_jobs,
            "status_distribution": status_counts,
            "average_processing_time": sum(processing_times) / len(processing_times) if processing_times else 0,
            "total_files_processed": total_files,
            "active_workers": self.max_workers,
            "queue_size": self.processing_queue.qsize() if hasattr(self.processing_queue, 'qsize') else 0
        }
